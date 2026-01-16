# ARES Quick Start Guide

Get ARES up and running in 5 minutes!

## Prerequisites

- Python 3.12 or higher
- Ollama installed ([Download Ollama](https://ollama.ai/))

## Step 1: Install Dependencies

### Windows (PowerShell)
```powershell
.\setup.ps1
```

### Linux/Mac (Bash)
```bash
chmod +x setup.sh
./setup.sh
```

### Manual Installation
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download German spaCy model
python -m spacy download de_core_news_sm

# Create directories
mkdir -p data chroma_db uploads

# Copy environment file
cp .env.example .env
```

## Step 2: Start Ollama

```bash
# Start Ollama service
ollama serve
```

In a new terminal, pull the required models:

```bash
ollama pull llama3:8b
ollama pull mxbai-embed-large
```

**Note**: Model downloads can take several minutes depending on your internet connection.

## Step 3: Verify Setup

```bash
# Check Ollama connection and models
python scripts/check_ollama.py

# Initialize database
python scripts/init_db.py
```

## Step 4: Start ARES

### Option A: Development Mode (Recommended for first run)

**Terminal 1 - Backend:**
```bash
uvicorn src.api.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
streamlit run src/ui/app.py
```

### Option B: Docker (Production-like)

```bash
docker-compose up -d
```

## Step 5: Access ARES

- **Frontend UI**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## First Steps

1. **Upload a Document**
   - Click "Upload Documents" in the sidebar
   - Select a PDF, DOCX, TXT, MD, or XLSX file
   - Click "Upload & Index"
   - Wait for indexing to complete

2. **Ask a Question**
   - Type your question in the chat interface
   - ARES will search your documents and provide an answer
   - View citations and confidence scores

3. **Check Privacy Status**
   - Look for the PII masking indicator
   - Review detected PII entities in the sidebar

## Troubleshooting

### Ollama Connection Issues

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start it
ollama serve
```

### Model Not Found

```bash
# List available models
ollama list

# Pull missing models
ollama pull llama3:8b
ollama pull mxbai-embed-large
```

### Database Issues

```bash
# Reinitialize database
python scripts/init_db.py

# Check database location
ls -la chroma_db/
```

### Port Already in Use

If port 8000 or 8501 is already in use:

```bash
# Backend on different port
uvicorn src.api.main:app --reload --port 8001

# Frontend on different port
streamlit run src/ui/app.py --server.port 8502
```

Update `.env` or Streamlit config accordingly.

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Review [DSGVO_KONFORMITÄT.md](DSGVO_KONFORMITÄT.md) for GDPR compliance details
- Explore the API at http://localhost:8000/docs
- Check out the test suite: `pytest`

## Getting Help

- Check logs in the terminal for error messages
- Review the API documentation at `/docs`
- Verify all services are running with the health check endpoint

---

**Welcome to ARES! 🛡️**
