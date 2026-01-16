#!/usr/bin/env python3
"""
Python API client for ARES with retry logic and error handling.
"""

import httpx
import time
from typing import Optional, Dict, Any, List
from pathlib import Path
from loguru import logger


class ARESClient:
    """Client for interacting with ARES API."""

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        timeout: float = 120.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        """
        Initialize ARES client.

        Args:
            base_url: Base URL of ARES API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.api_url = f"{self.base_url}/api/v1"
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs,
    ) -> httpx.Response:
        """
        Make HTTP request with retry logic.

        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional request arguments

        Returns:
            HTTP response
        """
        url = f"{self.api_url}{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    response = client.request(method, url, **kwargs)
                    response.raise_for_status()
                    return response
            except httpx.TimeoutException:
                if attempt < self.max_retries - 1:
                    logger.warning(f"Request timeout, retrying... ({attempt + 1}/{self.max_retries})")
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    raise
            except httpx.HTTPStatusError as e:
                if e.response.status_code >= 500 and attempt < self.max_retries - 1:
                    logger.warning(f"Server error, retrying... ({attempt + 1}/{self.max_retries})")
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    raise
            except Exception as e:
                logger.error(f"Request failed: {e}")
                raise

    def health_check(self) -> Dict[str, Any]:
        """Check API health status."""
        response = self._request("GET", "/health")
        return response.json()

    def query(
        self,
        query: str,
        mask_pii: bool = True,
    ) -> Dict[str, Any]:
        """
        Query documents.

        Args:
            query: Search query
            mask_pii: Enable PII masking

        Returns:
            Query response with answer and citations
        """
        response = self._request(
            "POST",
            "/query",
            json={"query": query, "mask_pii": mask_pii},
        )
        return response.json()

    def upload_document(
        self,
        file_path: str,
        progress_callback: Optional[callable] = None,
    ) -> Dict[str, Any]:
        """
        Upload and index a document.

        Args:
            file_path: Path to document file
            progress_callback: Optional callback for progress updates

        Returns:
            Upload response with document ID and metadata
        """
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, "rb") as f:
            files = {"file": (file_path_obj.name, f, "application/octet-stream")}
            response = self._request("POST", "/upload", files=files)

        return response.json()

    def delete_document(self, document_id: str) -> Dict[str, Any]:
        """Delete a document from the index."""
        response = self._request("DELETE", f"/documents/{document_id}")
        return response.json()

    def detect_pii(self, text: str) -> Dict[str, Any]:
        """Detect PII in text."""
        response = self._request(
            "POST",
            "/pii/detect",
            json={"text": text},
        )
        return response.json()

    def mask_pii(self, text: str) -> Dict[str, Any]:
        """Mask PII in text."""
        response = self._request(
            "POST",
            "/pii/mask",
            json={"text": text},
        )
        return response.json()

    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        response = self._request("GET", "/stats")
        return response.json()

    def get_metrics(self) -> Dict[str, Any]:
        """Get API metrics."""
        response = self._request("GET", "/metrics")
        return response.json()


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = ARESClient(base_url="http://localhost:8000")

    # Health check
    print("Health Check:")
    health = client.health_check()
    print(f"Status: {health.get('status')}")

    # Query documents
    print("\nQuery Example:")
    result = client.query("What is the main topic?")
    print(f"Answer: {result['answer'][:100]}...")
    print(f"Confidence: {result['confidence']:.2%}")

    # Get stats
    print("\nStatistics:")
    stats = client.get_stats()
    print(f"Documents: {stats['documents_indexed']}")
    print(f"Chunks: {stats['chunks_indexed']}")
