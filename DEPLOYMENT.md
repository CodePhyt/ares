# ARES Deployment Guide

Complete guide for deploying ARES in production environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Docker Deployment](#docker-deployment)
4. [Manual Deployment](#manual-deployment)
5. [Production Configuration](#production-configuration)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **CPU**: 4+ cores recommended (8+ for production)
- **RAM**: 16GB minimum (32GB+ recommended)
- **Storage**: 50GB+ free space (SSD recommended)
- **OS**: Linux (Ubuntu 20.04+, Debian 11+), macOS, or Windows Server

### Software Requirements

- Python 3.12 or higher
- Docker & Docker Compose (for containerized deployment)
- Ollama (latest version)
- 20GB+ free disk space for models

## Environment Setup

### 1. Clone and Prepare

```bash
git clone <repository-url>
cd "Sentinel-Local-BI Ares"
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with production settings
```

**Critical Production Settings:**

```env
# Security
ENABLE_PII_MASKING=true
AUDIT_LOG_ENABLED=true

# Performance
CHUNK_SIZE=512
CHUNK_OVERLAP=50
TOP_K_DOCUMENTS=5

# Logging
LOG_LEVEL=INFO  # Use WARNING in production for less verbose logs

# Resource Limits
MAX_UPLOAD_SIZE=100MB
```

### 3. Install Ollama Models

```bash
# Start Ollama
ollama serve

# Pull required models (this may take 30+ minutes)
ollama pull llama3:8b
ollama pull mxbai-embed-large

# Verify models
ollama list
```

## Docker Deployment

### Quick Start

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### Production Docker Compose

For production, use a custom `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  ares-backend:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - LOG_LEVEL=WARNING
      - ENABLE_PII_MASKING=true
    volumes:
      - ./data:/app/data
      - ./chroma_db:/app/chroma_db
      - ./uploads:/app/uploads
      - ./logs:/app/logs
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
        reservations:
          cpus: '2'
          memory: 4G

  ollama:
    image: ollama/ollama:latest
    volumes:
      - ollama_data:/root/.ollama
    restart: always
    deploy:
      resources:
        limits:
          cpus: '8'
          memory: 16G
        reservations:
          cpus: '4'
          memory: 8G

  streamlit:
    build:
      context: .
      dockerfile: Dockerfile.streamlit
    environment:
      - BACKEND_URL=http://ares-backend:8000
    restart: always
    depends_on:
      - ares-backend

volumes:
  ollama_data:
```

Deploy with:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Manual Deployment

### 1. System Setup

```bash
# Create system user
sudo useradd -r -s /bin/false ares

# Create directories
sudo mkdir -p /opt/ares/{data,chroma_db,uploads,logs}
sudo chown -R ares:ares /opt/ares
```

### 2. Install Dependencies

```bash
# Create virtual environment
python3.12 -m venv /opt/ares/venv
source /opt/ares/venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
python -m spacy download de_core_news_sm
```

### 3. Systemd Service

Create `/etc/systemd/system/ares-backend.service`:

```ini
[Unit]
Description=ARES Backend API
After=network.target

[Service]
Type=simple
User=ares
WorkingDirectory=/opt/ares
Environment="PATH=/opt/ares/venv/bin"
ExecStart=/opt/ares/venv/bin/uvicorn src.api.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/ares-streamlit.service`:

```ini
[Unit]
Description=ARES Streamlit Frontend
After=network.target ares-backend.service
Requires=ares-backend.service

[Service]
Type=simple
User=ares
WorkingDirectory=/opt/ares
Environment="PATH=/opt/ares/venv/bin"
Environment="BACKEND_URL=http://localhost:8000"
ExecStart=/opt/ares/venv/bin/streamlit run src/ui/app.py \
    --server.port=8501 \
    --server.address=0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable ares-backend ares-streamlit
sudo systemctl start ares-backend ares-streamlit

# Check status
sudo systemctl status ares-backend
sudo systemctl status ares-streamlit
```

### 4. Reverse Proxy (Nginx)

Create `/etc/nginx/sites-available/ares`:

```nginx
upstream ares_backend {
    server localhost:8000;
}

upstream ares_frontend {
    server localhost:8501;
}

server {
    listen 80;
    server_name ares.example.com;

    # Frontend
    location / {
        proxy_pass http://ares_frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api {
        proxy_pass http://ares_backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Increase timeouts for long-running queries
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Health check
    location /health {
        proxy_pass http://ares_backend;
        access_log off;
    }
}
```

Enable and reload:

```bash
sudo ln -s /etc/nginx/sites-available/ares /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Production Configuration

### Security Hardening

1. **Firewall Configuration**

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

2. **SSL/TLS Setup**

Use Let's Encrypt with Certbot:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d ares.example.com
```

3. **Environment Variables**

Never commit `.env` files. Use secrets management:
- Docker secrets
- Kubernetes secrets
- HashiCorp Vault
- AWS Secrets Manager

### Performance Tuning

1. **Ollama Configuration**

Create `~/.ollama/config.json`:

```json
{
  "num_gpu": 1,
  "num_thread": 8,
  "numa": false
}
```

2. **ChromaDB Optimization**

For large datasets, consider:
- Increasing chunk size for better retrieval
- Adjusting embedding batch size
- Using SSD storage for ChromaDB

3. **API Workers**

Adjust workers based on CPU cores:

```bash
# For 8-core system
uvicorn src.api.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

## Monitoring & Maintenance

### Health Checks

Set up automated health checks:

```bash
# Cron job for health monitoring
*/5 * * * * /opt/ares/venv/bin/python /opt/ares/scripts/health_check.py --exit-code >> /var/log/ares-health.log 2>&1
```

### Log Rotation

Create `/etc/logrotate.d/ares`:

```
/opt/ares/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0640 ares ares
}
```

### Backup Strategy

1. **Database Backup**

```bash
# Daily backup script
#!/bin/bash
BACKUP_DIR="/opt/ares/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Export data
python /opt/ares/scripts/export_data.py --output "$BACKUP_DIR/ares_$DATE.json"

# Backup ChromaDB
tar -czf "$BACKUP_DIR/chromadb_$DATE.tar.gz" /opt/ares/chroma_db

# Keep only last 30 days
find $BACKUP_DIR -type f -mtime +30 -delete
```

2. **Automated Backups**

Add to crontab:

```bash
0 2 * * * /opt/ares/scripts/backup.sh
```

### Metrics Monitoring

Access metrics endpoint:

```bash
curl http://localhost:8000/api/v1/metrics | jq
```

Set up monitoring with:
- Prometheus + Grafana
- Datadog
- New Relic
- Custom monitoring scripts

## Troubleshooting

### Common Issues

1. **Ollama Connection Failed**

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
sudo systemctl restart ollama
```

2. **Out of Memory**

- Reduce `CHUNK_SIZE` in `.env`
- Reduce number of workers
- Increase system RAM
- Use model quantization

3. **Slow Queries**

- Check Ollama GPU utilization
- Optimize ChromaDB indexes
- Increase `TOP_K_DOCUMENTS` for better results
- Check network latency

4. **Database Corruption**

```bash
# Reinitialize database
python scripts/init_db.py

# Restore from backup if needed
tar -xzf backups/chromadb_YYYYMMDD.tar.gz -C /opt/ares/
```

### Log Analysis

```bash
# View recent errors
grep ERROR /opt/ares/logs/*.log | tail -20

# Monitor real-time logs
tail -f /opt/ares/logs/backend.log
```

### Performance Profiling

```bash
# Check API response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/health

# Monitor system resources
htop
iostat -x 1
```

## Scaling

### Horizontal Scaling

For high-traffic scenarios:

1. **Load Balancer**: Use Nginx or HAProxy
2. **Multiple Backend Instances**: Run multiple API workers
3. **Shared Storage**: Use network storage for ChromaDB
4. **Caching Layer**: Add Redis for query caching

### Vertical Scaling

- Increase RAM for larger document collections
- Use GPU for faster Ollama inference
- SSD storage for better I/O performance

## Disaster Recovery

1. **Regular Backups**: Daily automated backups
2. **Backup Testing**: Regularly test restore procedures
3. **Documentation**: Maintain runbooks for common scenarios
4. **Monitoring**: Set up alerts for critical failures

---

For additional support, refer to:
- [README.md](README.md) - General documentation
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [DSGVO_KONFORMITÄT.md](DSGVO_KONFORMITÄT.md) - GDPR compliance
