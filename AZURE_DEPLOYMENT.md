# Azure Deployment Guide for CDCNSA

## Prerequisites
- GitHub Education account (for Azure for Students)
- Azure for Students account ($100 free credit, no credit card)

## Step 1: Claim Azure for Students
1. Go to https://azure.microsoft.com/en-us/free/students/
2. Click "Start free"
3. Sign in with your GitHub account
4. Verify through GitHub Education (no credit card needed)
5. You'll get $100 credit valid for 12 months

## Step 2: Create Azure App Service

### Option A: Via Azure Portal (Easiest)
1. Go to https://portal.azure.com
2. Click "Create a resource" → "Web App"
3. Configure:
   - **Name**: `cdcnsa-app` (or any unique name)
   - **Publish**: Code
   - **Runtime**: Python 3.11
   - **Region**: Choose closest to you
   - **Pricing**: Select "Free F1" or "Shared D1" tier (uses your $100 credit)
   - **Instance**: If available, choose Basic B1 (2GB RAM) for better performance
4. Click "Review + create" → "Create"

### Option B: Via Azure CLI
```bash
# Install Azure CLI: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
az login

# Create resource group
az group create --name cdcnsa-rg --location "East US"

# Create App Service plan (Free tier)
az appservice plan create --name cdcnsa-plan --resource-group cdcnsa-rg --sku FREE --is-linux

# Create web app
az webapp create --name cdcnsa-app --resource-group cdcnsa-rg --plan cdcnsa-plan --runtime "PYTHON:3.11"

# Configure app settings
az webapp config appsettings set --name cdcnsa-app --resource-group cdcnsa-rg --settings \
  PYTHON_VERSION=3.11 \
  PORT=8000 \
  GROQ_API_KEY="your-groq-api-key-here"
```

## Step 3: Configure GitHub Secrets

1. Go to your GitHub repo: https://github.com/ayesha-yousaf5/CDCNSA
2. Click "Settings" → "Secrets and variables" → "Actions"
3. Add these secrets:

### AZURE_CREDENTIALS
Generate Azure credentials:
```bash
# In Azure Cloud Shell or local terminal with Azure CLI
az ad sp create-for-rbac --name "cdcnsa-github" --role contributor \
  --scopes /subscriptions/{subscription-id}/resourceGroups/cdcnsa-rg \
  --sdk-auth
```

This outputs JSON like:
```json
{
  "clientId": "xxxx",
  "clientSecret": "xxxx",
  "subscriptionId": "xxxx",
  "tenantId": "xxxx"
}
```

Copy the entire JSON output and paste it as the `AZURE_CREDENTIALS` secret in GitHub.

### GROQ_API_KEY
- Go to https://console.groq.com
- Copy your API key
- Add as `GROQ_API_KEY` secret in GitHub

## Step 4: Update Workflow Configuration

Edit `.github/workflows/azure-deploy.yml`:
- Change `AZURE_WEBAPP_NAME` to match your Azure App Service name (e.g., `cdcnsa-app`)

## Step 5: Deploy

```bash
# Commit and push the Azure config files
git add .github/workflows/azure-deploy.yml startup.sh
git commit -m "Add Azure deployment configuration"
git push origin main
```

The GitHub Action will automatically deploy to Azure.

## Step 6: Verify Deployment

1. Go to https://cdcnsa-app.azurewebsites.net (replace with your app name)
2. Check the health endpoint: https://cdcnsa-app.azurewebsites.net/api/health
3. Test the diagnosis and chatbot features

## Troubleshooting

### Check logs
```bash
# Via Azure CLI
az webapp log tail --name cdcnsa-app --resource-group cdcnsa-rg

# Or via Azure Portal:
# App Service → Log stream
```

### Restart the app
```bash
az webapp restart --name cdcnsa-app --resource-group cdcnsa-rg
```

### Increase memory (if needed)
If you get OOM errors, upgrade to a higher tier:
```bash
az appservice plan update --name cdcnsa-plan --resource-group cdcnsa-rg --sku B1
```

## Cost Management

- Monitor your Azure spending: https://portal.azure.com/#view/Microsoft_Azure_CostManagement/Overview
- Set up budget alerts to avoid unexpected charges
- The Free tier should be sufficient for demo purposes
- Your $100 credit lasts 12 months

## Advantages Over Render Free Tier

✅ No cold starts or spin-down
✅ More RAM (2GB+ on Basic tier)
✅ Stable performance
✅ No 502 errors
✅ Full control over startup process
✅ Better for ML workloads

## Next Steps

After deployment:
1. Test all features (diagnosis, chatbot, voice)
2. Monitor logs for any errors
3. Set up custom domain (optional, free with GitHub Education)
4. Configure SSL (automatic on Azure)
