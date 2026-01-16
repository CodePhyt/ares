#!/usr/bin/env python3
"""
Utility script to check Ollama connection and model availability.
"""

import sys
import httpx
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.config import settings


def check_ollama_connection():
    """Check if Ollama is running and accessible."""
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
            if response.status_code == 200:
                print("✅ Ollama is running and accessible")
                return True
            else:
                print(f"❌ Ollama returned status code: {response.status_code}")
                return False
    except httpx.ConnectError:
        print(f"❌ Cannot connect to Ollama at {settings.OLLAMA_BASE_URL}")
        print("   Make sure Ollama is running: ollama serve")
        return False
    except Exception as e:
        print(f"❌ Error checking Ollama: {e}")
        return False


def check_models():
    """Check if required models are available."""
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
            if response.status_code != 200:
                print("❌ Cannot fetch model list")
                return False

            models = response.json().get("models", [])
            model_names = [model.get("name", "") for model in models]

            required_models = [
                settings.OLLAMA_MODEL,
                settings.OLLAMA_EMBEDDING_MODEL,
            ]

            all_available = True
            for model in required_models:
                # Check if model name matches (with or without tag)
                found = any(model in name or name.startswith(model.split(":")[0]) for name in model_names)
                if found:
                    print(f"✅ Model available: {model}")
                else:
                    print(f"❌ Model missing: {model}")
                    print(f"   Install with: ollama pull {model}")
                    all_available = False

            return all_available

    except Exception as e:
        print(f"❌ Error checking models: {e}")
        return False


def test_embedding():
    """Test embedding generation."""
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{settings.OLLAMA_BASE_URL}/api/embeddings",
                json={
                    "model": settings.OLLAMA_EMBEDDING_MODEL,
                    "prompt": "Test embedding",
                },
            )
            if response.status_code == 200:
                embedding = response.json().get("embedding", [])
                print(f"✅ Embedding test successful (dimension: {len(embedding)})")
                return True
            else:
                print(f"❌ Embedding test failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Error testing embedding: {e}")
        return False


def main():
    """Run all checks."""
    print("🛡️ ARES - Ollama Connection Check")
    print("=" * 40)
    print(f"Ollama URL: {settings.OLLAMA_BASE_URL}")
    print(f"LLM Model: {settings.OLLAMA_MODEL}")
    print(f"Embedding Model: {settings.OLLAMA_EMBEDDING_MODEL}")
    print()

    connection_ok = check_ollama_connection()
    if not connection_ok:
        sys.exit(1)

    print()
    models_ok = check_models()
    print()

    if models_ok:
        print("Testing embedding generation...")
        embedding_ok = test_embedding()
        print()

        if embedding_ok:
            print("✅ All checks passed!")
            sys.exit(0)
        else:
            print("❌ Embedding test failed")
            sys.exit(1)
    else:
        print("❌ Some models are missing")
        sys.exit(1)


if __name__ == "__main__":
    main()
