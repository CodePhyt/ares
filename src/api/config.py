"""
Configuration management using Pydantic Settings.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Ollama Configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3:8b"
    OLLAMA_EMBEDDING_MODEL: str = "mxbai-embed-large"

    # ChromaDB Configuration
    CHROMA_DB_PATH: str = "./chroma_db"
    CHROMA_COLLECTION_NAME: str = "ares_documents"

    # Application Settings
    LOG_LEVEL: str = "INFO"
    MAX_UPLOAD_SIZE: str = "100MB"
    ALLOWED_EXTENSIONS: str = "pdf,docx,txt,md,xlsx"

    # Privacy & Security
    ENABLE_PII_MASKING: bool = True
    PII_MASKING_STRATEGY: str = "replace"
    AUDIT_LOG_ENABLED: bool = True

    # RAG Configuration
    TOP_K_DOCUMENTS: int = 5
    TOP_K_PARENTS: int = 3
    RERANK_TOP_K: int = 3
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50

    # Agent Configuration
    ENABLE_REASONING_AGENT: bool = True
    MAX_ITERATIONS: int = 5
    TEMPERATURE: float = 0.1

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
