# ARES Docker Quickstart

**Deploy ARES in exactly 2 commands!**

## 🚀 Quick Deployment

### Prerequisites
- Docker and Docker Compose installed
- 20GB+ free disk space (for Ollama models)

### Step 1: Start Services

```bash
docker-compose up -d
```

This command will:
- ✅ Pull required Docker images
- ✅ Start Ollama service
- ✅ Start ARES backend API
- ✅ Start Streamlit frontend
- ✅ Configure networking between services

### Step 2: Initialize Models

```bash
docker exec ares-ollama ollama pull llama3:8b && docker exec ares-ollama ollama pull mxbai-embed-large
```

This command will:
- ✅ Download Llama-3-8B model (~4.7GB)
- ✅ Download mxbai-embed-large model (~670MB)
- ✅ Make models available to ARES

**Total time**: ~10-15 minutes (depending on internet speed)

## 🎯 Access ARES

Once both commands complete:

- **Frontend UI**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📋 What's Running?

After deployment, you'll have:

1. **Ollama Service** (Port 11434)
   - Local LLM inference
   - Model storage

2. **ARES Backend** (Port 8000)
   - FastAPI REST API
   - RAG engine
   - PII masking

3. **ARES Frontend** (Port 8501)
   - Streamlit UI
   - Analytics dashboard
   - Document management

## 🔍 Verify Deployment

Check service status:

```bash
docker-compose ps
```

View logs:

```bash
docker-compose logs -f
```

## 🛑 Stop Services

```bash
docker-compose down
```

## 💾 Data Persistence

All data is stored in local volumes:
- `chroma_db/` - Vector database
- `uploads/` - Uploaded documents
- `ollama_data/` - Ollama models (persistent)

## 🔧 Troubleshooting

### Models Not Found

If queries fail, verify models are loaded:

```bash
docker exec ares-ollama ollama list
```

### Port Conflicts

If ports 8000 or 8501 are in use, edit `docker-compose.yml`:

```yaml
ports:
  - "8001:8000"  # Change 8000 to 8001
```

### Out of Memory

If services crash, increase Docker memory limit:
- Docker Desktop: Settings > Resources > Memory
- Minimum: 8GB recommended

## 📚 Next Steps

1. **Upload Documents**: Use the Streamlit UI to upload PDF, DOCX, TXT, MD, or XLSX files
2. **Query Documents**: Ask questions about your indexed documents
3. **View Analytics**: Check the Analytics tab for system health
4. **Explore Relationships**: Use Discovery tab to see document connections

## 🎉 That's It!

ARES is now running and ready to use. For detailed configuration, see [DEPLOYMENT.md](DEPLOYMENT.md).

---

**Need help?** Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) or review logs with `docker-compose logs -f`.
