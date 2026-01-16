#!/bin/bash
# ARES Setup Script

echo "🛡️ ARES Setup - Autonomous Resilient Enterprise Suite"
echo "=================================================="

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Download German spaCy model
echo "Downloading German spaCy model for Presidio..."
python -m spacy download de_core_news_sm

# Create necessary directories
echo "Creating data directories..."
mkdir -p data chroma_db uploads

# Copy .env if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your configuration"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Start Ollama: ollama serve"
echo "2. Pull models: ollama pull llama3:8b && ollama pull mxbai-embed-large"
echo "3. Start backend: uvicorn src.api.main:app --reload"
echo "4. Start frontend: streamlit run src/ui/app.py"
echo ""
