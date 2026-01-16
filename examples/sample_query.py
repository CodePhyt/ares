#!/usr/bin/env python3
"""
Example script demonstrating how to use the ARES API programmatically.
"""

import httpx
import json
from pathlib import Path


# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"


def query_documents(query: str, mask_pii: bool = True) -> dict:
    """Query documents using ARES."""
    with httpx.Client(timeout=120.0) as client:
        response = client.post(
            f"{API_BASE_URL}/query",
            json={"query": query, "mask_pii": mask_pii},
        )
        response.raise_for_status()
        return response.json()


def upload_document(file_path: str) -> dict:
    """Upload a document to ARES."""
    file_path_obj = Path(file_path)
    
    if not file_path_obj.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with httpx.Client(timeout=300.0) as client:
        with open(file_path, "rb") as f:
            files = {"file": (file_path_obj.name, f, "application/octet-stream")}
            response = client.post(f"{API_BASE_URL}/upload", files=files)
            response.raise_for_status()
            return response.json()


def detect_pii(text: str) -> dict:
    """Detect PII in text."""
    with httpx.Client(timeout=30.0) as client:
        response = client.post(
            f"{API_BASE_URL}/pii/detect",
            json={"text": text},
        )
        response.raise_for_status()
        return response.json()


def get_stats() -> dict:
    """Get system statistics."""
    with httpx.Client(timeout=10.0) as client:
        response = client.get(f"{API_BASE_URL}/stats")
        response.raise_for_status()
        return response.json()


def main():
    """Example usage."""
    print("🛡️ ARES API Example")
    print("=" * 40)
    
    # 1. Check system stats
    print("\n1. System Statistics:")
    try:
        stats = get_stats()
        print(json.dumps(stats, indent=2))
    except Exception as e:
        print(f"Error: {e}")
    
    # 2. Detect PII in sample text
    print("\n2. PII Detection Example:")
    sample_text = "Contact Max Mustermann at max.mustermann@example.com or call +49 123 456789"
    try:
        pii_result = detect_pii(sample_text)
        print(f"Total PII detected: {pii_result['total_pii']}")
        print(f"Entities: {pii_result['entity_breakdown']}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 3. Upload a document (if file exists)
    print("\n3. Document Upload Example:")
    sample_file = "example_document.pdf"
    if Path(sample_file).exists():
        try:
            upload_result = upload_document(sample_file)
            print(f"Document ID: {upload_result['document_id']}")
            print(f"Chunks created: {upload_result['chunks_created']}")
            print(f"PII detected: {upload_result['pii_detected']}")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print(f"Sample file '{sample_file}' not found. Skipping upload example.")
    
    # 4. Query documents
    print("\n4. Query Example:")
    query = "What is the main topic of the documents?"
    try:
        query_result = query_documents(query)
        print(f"Answer: {query_result['answer'][:200]}...")
        print(f"Confidence: {query_result['confidence']:.2%}")
        print(f"Citations: {len(query_result['citations'])}")
        print(f"Iterations: {query_result['iterations']}")
    except Exception as e:
        print(f"Error: {e}")
        print("Note: Make sure you have uploaded documents first!")


if __name__ == "__main__":
    main()
