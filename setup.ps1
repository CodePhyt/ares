# ARES Setup Script for Windows PowerShell

Write-Host "🛡️ ARES Setup - Autonomous Resilient Enterprise Suite" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# Check Python version
$pythonVersion = python --version
Write-Host "Python version: $pythonVersion"

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install --upgrade pip
pip install -r requirements.txt

# Download German spaCy model
Write-Host "Downloading German spaCy model for Presidio..." -ForegroundColor Yellow
python -m spacy download de_core_news_sm

# Create necessary directories
Write-Host "Creating data directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path data, chroma_db, uploads | Out-Null

# Copy .env if it doesn't exist
if (-not (Test-Path .env)) {
    Write-Host "Creating .env file from .env.example..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "⚠️  Please edit .env with your configuration" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Start Ollama: ollama serve"
Write-Host "2. Pull models: ollama pull llama3:8b && ollama pull mxbai-embed-large"
Write-Host "3. Start backend: uvicorn src.api.main:app --reload"
Write-Host "4. Start frontend: streamlit run src/ui/app.py"
Write-Host ""
