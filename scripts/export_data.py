#!/usr/bin/env python3
"""
Export ARES data for backup or migration.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.config import settings
from src.core.rag_engine import HybridRAGEngine
from loguru import logger


def export_documents(output_file: Path) -> Dict[str, Any]:
    """Export all documents metadata."""
    try:
        rag_engine = HybridRAGEngine(
            chroma_db_path=settings.CHROMA_DB_PATH,
            collection_name=settings.CHROMA_COLLECTION_NAME,
            ollama_base_url=settings.OLLAMA_BASE_URL,
            embedding_model=settings.OLLAMA_EMBEDDING_MODEL,
        )
        
        # Get all documents
        results = rag_engine.collection.get()
        
        # Group by document_id
        documents = {}
        if results.get("ids") and results.get("metadatas"):
            for i, chunk_id in enumerate(results["ids"]):
                metadata = results["metadatas"][i]
                doc_id = metadata.get("document_id", "unknown")
                
                if doc_id not in documents:
                    documents[doc_id] = {
                        "document_id": doc_id,
                        "filename": metadata.get("filename", "Unknown"),
                        "file_type": metadata.get("file_type", "unknown"),
                        "chunks": [],
                        "total_chunks": 0,
                    }
                
                documents[doc_id]["chunks"].append({
                    "chunk_id": chunk_id,
                    "chunk_index": metadata.get("chunk_index", 0),
                    "page": metadata.get("page", "N/A"),
                })
                documents[doc_id]["total_chunks"] += 1
        
        # Prepare export data
        export_data = {
            "export_date": datetime.now().isoformat(),
            "version": "1.0.0",
            "total_documents": len(documents),
            "total_chunks": len(results.get("ids", [])),
            "documents": list(documents.values()),
        }
        
        # Write to file
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info("Exported {} documents to {}", len(documents), output_file)
        return export_data
        
    except Exception as e:
        logger.error("Error exporting data: {}", e)
        raise


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Export ARES data")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(f"ares_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"),
        help="Output file path",
    )
    
    args = parser.parse_args()
    
    print("🛡️ ARES - Data Export")
    print("=" * 40)
    print(f"Output file: {args.output}")
    print()
    
    try:
        export_data = export_documents(args.output)
        
        print("✅ Export completed!")
        print(f"   Documents: {export_data['total_documents']}")
        print(f"   Chunks: {export_data['total_chunks']}")
        print(f"   File: {args.output}")
        
    except Exception as e:
        print(f"❌ Export failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
