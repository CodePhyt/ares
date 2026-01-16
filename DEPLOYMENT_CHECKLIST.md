# ARES Enterprise Deployment Checklist

## ✅ Pre-Deployment Checklist

### Environment Setup
- [ ] Docker and Docker Compose installed
- [ ] 20GB+ free disk space available
- [ ] Minimum 8GB RAM allocated to Docker
- [ ] Ports 8000, 8501, and 11434 available

### Dependencies
- [ ] All Python dependencies installed (`pip install -r requirements.txt`)
- [ ] German spaCy model downloaded (`python -m spacy download de_core_news_sm`)
- [ ] Ollama installed and running
- [ ] Required Ollama models pulled:
  - [ ] `llama3:8b`
  - [ ] `mxbai-embed-large`

### Configuration
- [ ] Environment variables configured (if needed)
- [ ] `.env` file created (if using custom settings)
- [ ] ChromaDB directory permissions set correctly
- [ ] Exports directory created (`mkdir exports`)

## 🚀 Deployment Steps

### Option 1: Docker Deployment (Recommended)
```bash
# Step 1: Start all services
docker-compose up -d

# Step 2: Initialize models
docker exec ares-ollama ollama pull llama3:8b && docker exec ares-ollama ollama pull mxbai-embed-large
```

### Option 2: Manual Deployment
```bash
# Backend
cd src/api
uvicorn main:app --host 0.0.0.0 --port 8000

# Frontend (separate terminal)
streamlit run src/ui/app.py --server.port 8501
```

## ✅ Post-Deployment Verification

### Service Health Checks
- [ ] Backend API accessible: http://localhost:8000/health
- [ ] Frontend UI accessible: http://localhost:8501
- [ ] API docs accessible: http://localhost:8000/docs
- [ ] Ollama service running: `docker ps` or `ollama list`

### Feature Verification
- [ ] **Query Interface**: Can submit queries and receive responses
- [ ] **Document Upload**: Can upload and index documents
- [ ] **Analytics Dashboard**: System health metrics display correctly
- [ ] **Discovery Tab**: Document graph visualizes relationships
- [ ] **PDF Export**: Can export audit reports as PDF
- [ ] **Theme Toggle**: Dark/Light mode switching works
- [ ] **Privacy Shield**: PII counter tracks masked entities

### Performance Checks
- [ ] Query response times < 10 seconds (typical)
- [ ] Memory usage within acceptable limits
- [ ] No error messages in logs
- [ ] System health endpoint returns valid data

## 🔧 Troubleshooting

### Common Issues

#### Models Not Found
```bash
# Verify models are loaded
docker exec ares-ollama ollama list

# Pull missing models
docker exec ares-ollama ollama pull llama3:8b
docker exec ares-ollama ollama pull mxbai-embed-large
```

#### Port Conflicts
- Edit `docker-compose.yml` to change ports
- Or stop conflicting services

#### Memory Issues
- Increase Docker memory limit (Settings > Resources > Memory)
- Minimum 8GB recommended

#### PDF Export Fails
- Ensure `exports/` directory exists and is writable
- Check backend logs for errors
- Verify ReportLab dependencies installed

## 📊 Monitoring

### Key Metrics to Monitor
- System memory usage
- Query response times
- Error rates
- PII masking statistics
- Document indexing success rate

### Log Locations
- Backend: Check Docker logs: `docker-compose logs -f ares-backend`
- Frontend: Check Streamlit logs
- Ollama: Check Docker logs: `docker-compose logs -f ares-ollama`

## 🎯 Production Readiness

### Security
- [ ] All secrets removed from code
- [ ] Environment variables properly configured
- [ ] Firewall rules configured
- [ ] SSL/TLS certificates (if exposing externally)

### Backup
- [ ] ChromaDB data backed up
- [ ] Configuration files backed up
- [ ] Export directory backed up

### Documentation
- [ ] Team trained on ARES usage
- [ ] Deployment procedures documented
- [ ] Troubleshooting guide available

## ✅ Success Criteria

ARES is successfully deployed when:
- ✅ All services are running
- ✅ Health checks pass
- ✅ Can upload and query documents
- ✅ Analytics dashboard displays metrics
- ✅ PDF export works correctly
- ✅ No critical errors in logs

---

**Deployment Date**: _______________
**Deployed By**: _______________
**Status**: ⬜ Pending | ⬜ In Progress | ⬜ Complete
