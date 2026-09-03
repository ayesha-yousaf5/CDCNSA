"""
Train corn severity classifier (MILD/MODERATE/SEVERE).
Uses EfficientNet-B0 with oversampling for class imbalance.
"""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler
from torchvision import transforms, models
import pandas as pd
import numpy as np
from pathlib import Path
from PIL import Image
from sklearn.metrics import classification_report, f1_score, accuracy_score
import json

# Config
SEVERITY_CLASSES = ['MILD', 'MODERATE', 'SEVERE']
CLASS_TO_IDX = {c: i for i, c in enumerate(SEVERITY_CLASSES)}
NUM_CLASSES = len(SEVERITY_CLASSES)
BATCH_SIZE = 32
NUM_EPOCHS = 10
LEARNING_RATE = 0.0003
IMAGE_SIZE = 224
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Paths
DATA_ROOT = Path(r'D:\plantdis\data\raw\hf\images')
SPLITS_CSV = Path(r'D:\plantdis\data\processed\splits.csv')
OUTPUT_DIR = Path(r'D:\hacathon\website deployment\plant_health_ai_professional_v6_mint_12crops_model_runtime\models\corn\severity')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Transforms
train_transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomVerticalFlip(),
    transforms.RandomRotation(20),
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

val_transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

class CornSeverityDataset(Dataset):
    def __init__(self, df, transform=None):
        self.df = df
        self.transform = transform
    
    def __len__(self):
        return len(self.df)
    
    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        # image_path is relative like 'data/raw/hf/images/xxx.jpg'
        img_path = Path(r'D:\plantdis') / row['image_path']
        image = Image.open(img_path).convert('RGB')
        label = CLASS_TO_IDX[row['severity']]
        
        if self.transform:
            image = self.transform(image)
        
        return image, label

def load_data():
    """Load corn severity data from splits.csv"""
    df = pd.read_csv(SPLITS_CSV)
    
    # Filter to corn only, exclude healthy (severity == NONE)
    corn_df = df[(df['crop'] == 'Corn') & (df['severity'] != 'NONE')].copy()
    
    print(f"Total corn diseased images: {len(corn_df)}")
    print(f"Severity distribution:\n{corn_df['severity'].value_counts()}")
    
    # Split into train/val (use existing split if available, else 80/20)
    if 'split' in corn_df.columns:
        train_df = corn_df[corn_df['split'] == 'train'].copy()
        val_df = corn_df[corn_df['split'] == 'val'].copy()
    else:
        # Random split
        np.random.seed(42)
        indices = np.random.permutation(len(corn_df))
        split_idx = int(0.8 * len(corn_df))
        train_df = corn_df.iloc[indices[:split_idx]].copy()
        val_df = corn_df.iloc[indices[split_idx:]].copy()
    
    print(f"\nTrain: {len(train_df)}, Val: {len(val_df)}")
    print(f"Train severity:\n{train_df['severity'].value_counts()}")
    print(f"Val severity:\n{val_df['severity'].value_counts()}")
    
    return train_df, val_df

def get_sampler(df):
    """Create weighted sampler for class imbalance"""
    labels = df['severity'].map(CLASS_TO_IDX).values
    class_counts = np.bincount(labels, minlength=NUM_CLASSES)
    class_weights = 1.0 / class_counts
    sample_weights = class_weights[labels]
    sampler = WeightedRandomSampler(sample_weights, len(sample_weights))
    return sampler

def train_model():
    print("Loading data...")
    train_df, val_df = load_data()
    
    train_dataset = CornSeverityDataset(train_df, train_transform)
    val_dataset = CornSeverityDataset(val_df, val_transform)
    
    train_sampler = get_sampler(train_df)
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, sampler=train_sampler, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)
    
    print(f"\nInitializing EfficientNet-B0 model...")
    model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.DEFAULT)
    model.classifier[1] = nn.Linear(model.classifier[1].in_features, NUM_CLASSES)
    model = model.to(DEVICE)
    
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max', factor=0.5, patience=2)
    
    best_f1 = 0.0
    best_epoch = 0
    
    print(f"\nTraining on {DEVICE}...")
    for epoch in range(NUM_EPOCHS):
        # Train
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0
        
        for images, labels in train_loader:
            images, labels = images.to(DEVICE), labels.to(DEVICE)
            
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            _, predicted = outputs.max(1)
            train_total += labels.size(0)
            train_correct += predicted.eq(labels).sum().item()
        
        train_acc = train_correct / train_total
        
        # Validate
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        all_preds = []
        all_labels = []
        
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(DEVICE), labels.to(DEVICE)
                outputs = model(images)
                loss = criterion(outputs, labels)
                
                val_loss += loss.item()
                _, predicted = outputs.max(1)
                val_total += labels.size(0)
                val_correct += predicted.eq(labels).sum().item()
                all_preds.extend(predicted.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
        
        val_acc = val_correct / val_total
        val_f1 = f1_score(all_labels, all_preds, average='macro')
        
        scheduler.step(val_f1)
        
        print(f"Epoch {epoch+1}/{NUM_EPOCHS} | "
              f"Train Loss: {train_loss/len(train_loader):.4f}, Train Acc: {train_acc:.4f} | "
              f"Val Loss: {val_loss/len(val_loader):.4f}, Val Acc: {val_acc:.4f}, Val F1: {val_f1:.4f}")
        
        if val_f1 > best_f1:
            best_f1 = val_f1
            best_epoch = epoch + 1
            # Save checkpoint
            checkpoint = {
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'epoch': epoch + 1,
                'val_f1': val_f1,
                'val_acc': val_acc,
                'class_to_idx': CLASS_TO_IDX,
                'architecture': 'efficientnet_b0',
                'backbone': 'efficientnet_b0',
                'severity_classes': SEVERITY_CLASSES,
            }
            torch.save(checkpoint, OUTPUT_DIR / 'corn_severity_efficientnet_b0_best.pt')
            print(f"  → Saved best model (F1: {val_f1:.4f})")
    
    print(f"\nTraining complete! Best epoch: {best_epoch}, Best F1: {best_f1:.4f}")
    print(f"Model saved to: {OUTPUT_DIR / 'corn_severity_efficientnet_b0_best.pt'}")
    
    # Final evaluation
    print("\nFinal validation report:")
    print(classification_report(all_labels, all_preds, target_names=SEVERITY_CLASSES))

if __name__ == '__main__':
    train_model()
