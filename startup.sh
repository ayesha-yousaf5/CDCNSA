#!/bin/bash

# Azure App Service startup script for CDCNSA

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Download models from Google Drive
python download_models.py

# Start the FastAPI server
# Azure sets PORT environment variable automatically
python -m uvicorn server:app --host 0.0.0.0 --port "$PORT"
