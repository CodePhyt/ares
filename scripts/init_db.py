#!/usr/bin/env python3
"""
Initialize ChromaDB database and verify setup.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.config import settings
from src.core.rag_engine import HybridRAGEngine
from loguru import logger


def initialize_database():
    """Initialize ChromaDB database."""
    print("🛡️ ARES - Database Initialization")
    print("=" * 40)
    
    try:
        # Create RAG engine (this will create the database if it doesn't exist)
        rag_engine = HybridRAGEngine(
            chroma_db_path=settings.CHROMA_DB_PATH,
            collection_name=settings.CHROMA_COLLECTION_NAME,
            ollama_base_url=settings.OLLAMA_BASE_URL,
            embedding_model=settings.OLLAMA_EMBEDDING_MODEL,
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )
        
        # Check if collection exists and has data
        try:
            results = rag_engine.collection.get()
            doc_count = len(set(
                meta.get("document_id", "unknown")
                for meta in results.get("metadatas", [])
            )) if results.get("metadatas") else 0
            
            chunk_count = len(results.get("ids", []))
            
            print(f"✅ Database initialized successfully")
            print(f"   Location: {settings.CHROMA_DB_PATH}")
            print(f"   Collection: {settings.CHROMA_COLLECTION_NAME}")
            print(f"   Documents: {doc_count}")
            print(f"   Chunks: {chunk_count}")
            
        except Exception as e:
            print(f"✅ Database created (empty)")
            print(f"   Location: {settings.CHROMA_DB_PATH}")
            print(f"   Collection: {settings.CHROMA_COLLECTION_NAME}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        logger.error(f"Database initialization failed: {e}")
        return False


def verify_directories():
    """Verify that required directories exist."""
    directories = [
        settings.CHROMA_DB_PATH,
        "./data",
        "./uploads",
    ]
    
    print("\n📁 Verifying directories...")
    all_exist = True
    
    for directory in directories:
        path = Path(directory)
        if path.exists():
            print(f"✅ {directory}")
        else:
            print(f"⚠️  {directory} (will be created on first use)")
            path.mkdir(parents=True, exist_ok=True)
    
    return all_exist


def main():
    """Run initialization."""
    if initialize_database():
        verify_directories()
        print("\n✅ Initialization complete!")
        sys.exit(0)
    else:
        print("\n❌ Initialization failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
