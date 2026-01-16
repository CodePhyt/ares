# ARES Troubleshooting Guide

Common issues and solutions for ARES deployment and operation.

## Quick Diagnosis

### Health Check

```bash
# Check overall health
python scripts/health_check.py

# Check Ollama
python scripts/check_ollama.py

# Check database
python scripts/init_db.py
```

## Common Issues

### 1. Ollama Connection Issues

**Symptoms:**
- `ConnectionError` when querying
- "Cannot connect to Ollama" errors
- Timeout errors

**Solutions:**

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama if not running
ollama serve

# Check Ollama logs
journalctl -u ollama -f  # systemd
# or
docker logs ares-ollama  # Docker

# Verify models are installed
ollama list

# Re-pull models if needed
ollama pull llama3:8b
ollama pull mxbai-embed-large
```

**Docker Environment:**
```bash
# Check Ollama container
docker ps | grep ollama

# Restart Ollama container
docker restart ares-ollama

# Check network connectivity
docker exec ares-backend curl http://ollama:11434/api/tags
```

### 2. Model Not Found Errors

**Symptoms:**
- "Model not found" errors
- Embedding generation fails

**Solutions:**

```bash
# List available models
ollama list

# Pull missing models
ollama pull llama3:8b
ollama pull mxbai-embed-large

# Verify model files
ls -lh ~/.ollama/models/
```

### 3. Out of Memory (OOM) Errors

**Symptoms:**
- Process killed
- "MemoryError" exceptions
- System becomes unresponsive

**Solutions:**

1. **Reduce Resource Usage:**
   ```env
   # In .env
   CHUNK_SIZE=256  # Reduce from 512
   TOP_K_DOCUMENTS=3  # Reduce from 5
   ```

2. **Limit Workers:**
   ```bash
   # Reduce API workers
   uvicorn src.api.main:app --workers 2
   ```

3. **Use Model Quantization:**
   ```bash
   # Use quantized models (smaller, faster)
   ollama pull llama3:8b-q4_0
   ```

4. **Increase System Memory:**
   - Add swap space
   - Upgrade RAM
   - Use smaller models

### 4. Slow Query Performance

**Symptoms:**
- Queries take >30 seconds
- Timeout errors
- High CPU usage

**Solutions:**

1. **Check System Resources:**
   ```bash
   htop
   iostat -x 1
   ```

2. **Optimize Configuration:**
   ```env
   # Reduce search scope
   TOP_K_DOCUMENTS=3
   RERANK_TOP_K=2
   ```

3. **Enable Caching:**
   - Use the cache utility for repeated queries
   - Implement Redis for distributed caching

4. **GPU Acceleration:**
   ```bash
   # Use GPU for Ollama (if available)
   CUDA_VISIBLE_DEVICES=0 ollama serve
   ```

5. **Database Optimization:**
   ```bash
   # Rebuild BM25 index
   # (happens automatically on document upload)
   ```

### 5. Database/ChromaDB Issues

**Symptoms:**
- "Collection not found" errors
- Corrupted database
- Missing documents

**Solutions:**

```bash
# Check database status
python scripts/init_db.py

# Check database files
ls -lh chroma_db/

# Reinitialize if corrupted
rm -rf chroma_db/
python scripts/init_db.py

# Restore from backup
tar -xzf backups/chromadb_YYYYMMDD.tar.gz
```

### 6. PII Detection Not Working

**Symptoms:**
- No PII detected when expected
- Presidio errors

**Solutions:**

```bash
# Verify spaCy model
python -c "import spacy; nlp = spacy.load('de_core_news_sm'); print('OK')"

# Reinstall spaCy model
python -m spacy download de_core_news_sm --force

# Test PII detection
python -c "
from src.security.pii_masker import GermanPIIMasker
masker = GermanPIIMasker()
result = masker.detect_pii('Contact Max Mustermann at max@example.com')
print(result)
"
```

### 7. File Upload Failures

**Symptoms:**
- Upload timeout
- "File too large" errors
- Unsupported format errors

**Solutions:**

1. **Check File Size:**
   ```env
   # Increase limit in .env
   MAX_UPLOAD_SIZE=200MB
   ```

2. **Check File Format:**
   ```bash
   # Verify file type
   file document.pdf
   
   # Check allowed extensions in .env
   ALLOWED_EXTENSIONS=pdf,docx,txt,md,xlsx
   ```

3. **Check Disk Space:**
   ```bash
   df -h
   # Ensure uploads/ directory has space
   ```

### 8. API Timeout Errors

**Symptoms:**
- 504 Gateway Timeout
- Request timeout errors

**Solutions:**

1. **Increase Timeouts:**
   ```nginx
   # In Nginx config
   proxy_read_timeout 600s;
   proxy_connect_timeout 75s;
   ```

2. **Check Query Complexity:**
   - Simplify queries
   - Reduce document search scope
   - Use more specific queries

### 9. Port Already in Use

**Symptoms:**
- "Address already in use" errors
- Cannot start services

**Solutions:**

```bash
# Find process using port
lsof -i :8000  # Backend
lsof -i :8501  # Frontend
lsof -i :11434 # Ollama

# Kill process
kill -9 <PID>

# Or change ports in .env
```

### 10. Docker Issues

**Symptoms:**
- Containers won't start
- Network connectivity issues
- Volume mount problems

**Solutions:**

```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs -f ares-backend

# Restart services
docker-compose restart

# Rebuild containers
docker-compose build --no-cache
docker-compose up -d

# Check volumes
docker volume ls
docker volume inspect <volume-name>

# Clean up
docker-compose down -v  # Removes volumes
docker system prune -a  # Clean up unused resources
```

## Performance Tuning

### Optimize for Large Document Collections

1. **Increase Chunk Size:**
   ```env
   CHUNK_SIZE=1024  # Larger chunks for better context
   CHUNK_OVERLAP=100
   ```

2. **Batch Processing:**
   ```bash
   # Use batch upload script
   python scripts/batch_upload.py /path/to/documents
   ```

3. **Index Optimization:**
   - Rebuild BM25 index periodically
   - Monitor ChromaDB size
   - Consider sharding for very large collections

### Optimize Query Performance

1. **Reduce Search Scope:**
   ```env
   TOP_K_DOCUMENTS=3
   TOP_K_PARENTS=2
   RERANK_TOP_K=2
   ```

2. **Enable Caching:**
   - Use cache decorator for frequent queries
   - Implement Redis for distributed caching

3. **Model Selection:**
   - Use quantized models for faster inference
   - Consider smaller models for simple queries

## Log Analysis

### View Logs

```bash
# Backend logs
tail -f logs/backend.log

# Docker logs
docker-compose logs -f ares-backend

# System logs
journalctl -u ares-backend -f
```

### Common Log Patterns

**High Error Rate:**
```bash
grep ERROR logs/*.log | wc -l
```

**Slow Queries:**
```bash
grep "Duration:" logs/*.log | awk '{print $NF}' | sort -n | tail -10
```

**Memory Issues:**
```bash
grep -i "memory\|oom\|killed" logs/*.log
```

## Getting Help

### Diagnostic Information

Collect diagnostic info:

```bash
# System info
uname -a
python --version
docker --version

# ARES status
python scripts/health_check.py --json > diagnostics.json
python scripts/check_ollama.py >> diagnostics.txt

# Logs
tar -czf logs.tar.gz logs/
```

### Support Resources

1. **Documentation:**
   - [README.md](README.md)
   - [QUICKSTART.md](QUICKSTART.md)
   - [DEPLOYMENT.md](DEPLOYMENT.md)

2. **Check Metrics:**
   ```bash
   curl http://localhost:8000/api/v1/metrics | jq
   ```

3. **Health Endpoint:**
   ```bash
   curl http://localhost:8000/health | jq
   ```

## Prevention

### Regular Maintenance

1. **Daily:**
   - Check health endpoint
   - Monitor disk space
   - Review error logs

2. **Weekly:**
   - Run cleanup script
   - Check backup status
   - Review metrics

3. **Monthly:**
   - Update dependencies
   - Review and optimize configuration
   - Test disaster recovery

### Monitoring Setup

Set up alerts for:
- High error rates
- Slow response times
- Low disk space
- Service downtime
- High memory usage

---

For deployment-specific issues, see [DEPLOYMENT.md](DEPLOYMENT.md).
