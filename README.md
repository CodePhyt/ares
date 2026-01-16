# ARES - Autonomous Resilient Enterprise Suite

**A GDPR-Compliant, 100% Offline AI Command Center for German Enterprises**

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)

## 🛡️ Overview

ARES is an enterprise-grade AI Command Center designed specifically for German enterprises that require **absolute data sovereignty** and **GDPR compliance**. Built with privacy-first principles, ARES enables organizations to index, search, and analyze sensitive documents using advanced AI capabilities—all while ensuring data never leaves your infrastructure.

### Key Features

- **🔒 100% Offline Operation**: All processing happens locally—no cloud dependencies
- **🛡️ GDPR-Compliant**: Automated PII detection and masking using Microsoft Presidio
- **🧠 Agentic Reasoning**: PLAN/SEARCH/AUDIT workflow for accurate, fact-checked responses
- **🔍 Hybrid Search**: Combines vector search (ChromaDB) with keyword search (BM25) for optimal retrieval
- **📊 Enterprise UI**: Professional Streamlit interface with real-time streaming and source citations
- **🇩🇪 German Language Support**: Full support for German text, including Umlauts

## 🏗️ Architecture

### Core Components

1. **Backend (FastAPI)**: Asynchronous REST API with comprehensive Swagger documentation
2. **RAG Engine**: Hybrid search combining:
   - Vector search via ChromaDB with `mxbai-embed-large` embeddings
   - Keyword search via BM25
   - Parent-Document-Retriever pattern for context preservation
   - Cross-Encoder re-ranking for relevance optimization
3. **Reasoning Agent**: LangGraph-based agent with:
   - **PLAN**: Determines if query requires document search
   - **SEARCH**: Executes hybrid RAG retrieval
   - **AUDIT**: Fact-checks answers against retrieved context
4. **Privacy Shield**: Microsoft Presidio integration for:
   - Names, Addresses, IBANs, Email detection
   - Automated masking before processing
   - Compliance auditing
5. **Frontend (Streamlit)**: Cyber-enterprise dark theme UI with:
   - Real-time token streaming
   - Source citations with file names/page numbers
   - Privacy status indicators

### Technology Stack

- **Python 3.12+**: Modern Python with type hints
- **FastAPI**: High-performance async web framework
- **Ollama**: Local LLM inference (Llama-3-8B & mxbai-embed-large)
- **ChromaDB**: Vector database for embeddings
- **LangChain/LangGraph**: Agent orchestration
- **Microsoft Presidio**: PII detection and anonymization
- **Streamlit**: Interactive web interface

## 🚀 Quick Start

> **New to ARES?** Check out the [Quick Start Guide](QUICKSTART.md) for a step-by-step walkthrough!

### Prerequisites

- Python 3.12 or higher
- Docker and Docker Compose (for containerized deployment)
- Ollama installed and running (see [Ollama Setup](#ollama-setup))

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "Sentinel-Local-BI Ares"
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download German spaCy model for Presidio**
   ```bash
   python -m spacy download de_core_news_sm
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Start Ollama and pull models**
   ```bash
   # Start Ollama service
   ollama serve
   
   # Pull required models (in another terminal)
   ollama pull llama3:8b
   ollama pull mxbai-embed-large
   ```

6. **Start the backend**
   ```bash
   uvicorn src.api.main:app --reload --port 8000
   ```

7. **Start the frontend** (in another terminal)
   ```bash
   streamlit run src/ui/app.py
   ```

8. **Access the application**
   - Frontend: http://localhost:8501
   - API Docs: http://localhost:8000/docs

### Docker Deployment

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 📖 Usage

### Uploading Documents

1. Navigate to the sidebar in the Streamlit UI
2. Click "Upload Documents"
3. Select a file (PDF, DOCX, TXT, MD, or XLSX)
4. Click "Upload & Index"
5. The document will be:
   - Scanned for PII
   - Chunked and indexed
   - Ready for querying

### Querying Documents

1. Enter your question in the chat interface
2. ARES will:
   - Plan the query strategy
   - Search relevant documents
   - Generate an answer
   - Audit for accuracy
3. View citations and confidence scores
4. Check PII masking status

### API Usage

#### Query Documents
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the main topic of the document?",
    "mask_pii": true
  }'
```

#### Upload Document
```bash
curl -X POST "http://localhost:8000/api/v1/upload" \
  -F "file=@document.pdf"
```

#### Batch Upload Documents
```bash
python scripts/batch_upload.py ./documents --api-url http://localhost:8000
```

#### Detect PII
```bash
curl -X POST "http://localhost:8000/api/v1/pii/detect" \
  -H "Content-Type: application/json" \
  -d '{"text": "Contact Max Mustermann at max@example.com"}'
```

#### Health Check
```bash
curl http://localhost:8000/health

# Or use the health check script
python scripts/health_check.py --api-url http://localhost:8000
```

#### Get Metrics
```bash
curl http://localhost:8000/api/v1/metrics
```

## 🔒 Privacy & Security

### Data Sovereignty

- **100% Local Processing**: All AI inference happens on your infrastructure
- **No External APIs**: No data sent to cloud services
- **Encrypted Storage**: ChromaDB data stored locally with access controls

### PII Protection

- **Automated Detection**: Microsoft Presidio detects:
  - Names (PERSON)
  - Email addresses
  - Phone numbers
  - IBAN codes
  - Physical addresses (LOCATION)
  - Credit card numbers
- **Masking Strategies**: Replace, hash, or encrypt sensitive data
- **Audit Logging**: Track all PII detection and masking events

### GDPR Compliance

ARES is designed with GDPR Article 25 (Data Protection by Design) in mind:

- **Privacy by Default**: PII masking enabled by default
- **Data Minimization**: Only necessary data is processed
- **Right to Erasure**: Documents can be deleted from the index
- **Audit Trails**: Comprehensive logging for compliance reporting

For detailed GDPR compliance information, see [DSGVO_KONFORMITÄT.md](DSGVO_KONFORMITÄT.md).

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_pii_masker.py
```

## 📁 Project Structure

```
.
├── src/
│   ├── api/              # FastAPI backend
│   │   ├── main.py      # Application entry point
│   │   ├── routes.py    # API endpoints
│   │   └── config.py    # Configuration
│   ├── core/            # Core functionality
│   │   ├── rag_engine.py        # Hybrid RAG engine
│   │   ├── agents.py            # Reasoning agent
│   │   └── document_processor.py # Document processing
│   ├── security/        # Privacy & security
│   │   └── pii_masker.py        # PII detection & masking
│   └── ui/              # Streamlit frontend
│       └── app.py       # Main UI application
├── scripts/             # Utility scripts
│   ├── check_ollama.py  # Ollama connection checker
│   ├── init_db.py       # Database initializer
│   ├── batch_upload.py  # Batch document upload
│   ├── export_data.py   # Export data for backup
│   ├── cleanup.py       # Cleanup old files
│   └── health_check.py  # Health check for monitoring
├── examples/            # Example scripts and data
│   ├── sample_query.py  # API usage examples
│   └── example_document.txt  # Sample document
├── tests/               # Test suite
├── docker-compose.yml   # Docker orchestration
├── Dockerfile           # Backend container
├── Dockerfile.streamlit # Frontend container
├── requirements.txt     # Python dependencies
├── pyproject.toml       # Modern Python project config
├── Makefile             # Common tasks
├── setup.sh             # Linux/Mac setup script
├── setup.ps1             # Windows setup script
├── QUICKSTART.md        # Quick start guide
├── CHANGELOG.md         # Version history
└── README.md           # This file
```

## ⚙️ Configuration

Key configuration options in `.env`:

```env
# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3:8b
OLLAMA_EMBEDDING_MODEL=mxbai-embed-large

# ChromaDB
CHROMA_DB_PATH=./chroma_db
CHROMA_COLLECTION_NAME=ares_documents

# Privacy
ENABLE_PII_MASKING=true
PII_MASKING_STRATEGY=replace

# RAG
TOP_K_DOCUMENTS=5
CHUNK_SIZE=512
CHUNK_OVERLAP=50
```

## 🤝 Contributing

This is a proprietary enterprise solution. For contributions or modifications, please contact the development team.

## 📄 License

Proprietary - All rights reserved.

## 🛠️ Development

### Common Tasks

Using Make (Linux/Mac):
```bash
make install      # Install dependencies
make test         # Run tests
make lint         # Run linters
make format       # Format code
make clean        # Clean generated files
```

Using Scripts:
```bash
# Check Ollama connection and models
python scripts/check_ollama.py

# Initialize database
python scripts/init_db.py

# Batch upload documents
python scripts/batch_upload.py /path/to/documents --api-url http://localhost:8000

# Export data for backup
python scripts/export_data.py --output backup.json

# Cleanup old files
python scripts/cleanup.py --uploads-age 30 --logs-age 7
```

### Code Quality

- **Type Hints**: Full type annotation coverage
- **Linting**: Ruff for fast linting
- **Formatting**: Black for consistent code style
- **Type Checking**: MyPy for static type analysis
- **Testing**: Pytest with coverage reporting

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed development guidelines.

## 📚 Additional Documentation

- **[QUICKSTART.md](QUICKSTART.md)**: Step-by-step setup guide
- **[DEPLOYMENT.md](DEPLOYMENT.md)**: Production deployment guide
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)**: Common issues and solutions
- **[DSGVO_KONFORMITÄT.md](DSGVO_KONFORMITÄT.md)**: GDPR compliance documentation
- **[CONTRIBUTING.md](CONTRIBUTING.md)**: Development guidelines
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)**: Project overview

## 🆘 Support

For technical support or questions:
- Review the [Quick Start Guide](QUICKSTART.md) for setup help
- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
- Review the [API Documentation](http://localhost:8000/docs) when running the backend
- Check [DSGVO_KONFORMITÄT.md](DSGVO_KONFORMITÄT.md) for GDPR compliance details
- Review logs in the application console

## 🙏 Acknowledgments

Built with:
- [Ollama](https://ollama.ai/) - Local LLM inference
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [Microsoft Presidio](https://github.com/microsoft/presidio) - PII detection
- [LangChain](https://www.langchain.com/) - LLM orchestration
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [Streamlit](https://streamlit.io/) - UI framework

---

**ARES v1.0.0** - Built for German Enterprise Data Sovereignty 🛡️
