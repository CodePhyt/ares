"""
FastAPI main application for ARES backend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

from src.api.routes import router
from src.api.config import settings
from src.api.middleware import (
    RequestIDMiddleware,
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
)
from src.api.rate_limit import rate_limit_middleware

# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL,
)

app = FastAPI(
    title="ARES API",
    description="Autonomous Resilient Enterprise Suite - GDPR-compliant AI Command Center",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Middleware (order matters - last added is first executed)
# Request ID should be first to tag all requests
app.add_middleware(RequestIDMiddleware)
# Rate limiting should be early to catch requests
app.middleware("http")(rate_limit_middleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api/v1", tags=["ARES"])


@app.get("/health")
async def health_check():
    """
    Health check endpoint with service status.
    """
    import httpx
    from pathlib import Path
    
    health_status = {
        "status": "healthy",
        "service": "ARES",
        "version": "1.0.0",
        "services": {},
    }
    
    # Check Ollama
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
            health_status["services"]["ollama"] = {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "url": settings.OLLAMA_BASE_URL,
            }
    except Exception as e:
        health_status["services"]["ollama"] = {
            "status": "unreachable",
            "error": str(e),
        }
        health_status["status"] = "degraded"
    
    # Check ChromaDB
    try:
        db_path = Path(settings.CHROMA_DB_PATH)
        health_status["services"]["chromadb"] = {
            "status": "healthy" if db_path.exists() else "not_initialized",
            "path": str(db_path),
        }
    except Exception as e:
        health_status["services"]["chromadb"] = {
            "status": "error",
            "error": str(e),
        }
        health_status["status"] = "degraded"
    
    return health_status


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("ARES Backend starting up...")
    logger.info("Ollama URL: {}", settings.OLLAMA_BASE_URL)
    logger.info("ChromaDB Path: {}", settings.CHROMA_DB_PATH)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("ARES Backend shutting down...")
