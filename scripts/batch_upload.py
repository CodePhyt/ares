#!/usr/bin/env python3
"""
Batch upload documents to ARES.
"""

import sys
import argparse
from pathlib import Path
from typing import List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
from loguru import logger

# Configure logger
logger.remove()
logger.add(sys.stderr, level="INFO")


def upload_file(file_path: Path, api_url: str) -> dict:
    """Upload a single file."""
    try:
        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f, "application/octet-stream")}
            
            with httpx.Client(timeout=300.0) as client:
                response = client.post(f"{api_url}/api/v1/upload", files=files)
                response.raise_for_status()
                return response.json()
    except Exception as e:
        logger.error("Error uploading {}: {}", file_path, e)
        return {"error": str(e), "filename": file_path.name}


def batch_upload(directory: Path, api_url: str, extensions: List[str] = None) -> dict:
    """Upload all files in a directory."""
    if extensions is None:
        extensions = ["pdf", "docx", "txt", "md", "xlsx"]
    
    results = {
        "success": [],
        "failed": [],
        "skipped": [],
    }
    
    # Find all files
    files = []
    for ext in extensions:
        files.extend(directory.glob(f"*.{ext}"))
        files.extend(directory.glob(f"*.{ext.upper()}"))
    
    if not files:
        logger.warning("No files found in {}", directory)
        return results
    
    logger.info("Found {} files to upload", len(files))
    
    for file_path in files:
        logger.info("Uploading: {}", file_path.name)
        result = upload_file(file_path, api_url)
        
        if "error" in result:
            results["failed"].append(result)
        elif result.get("status") == "success":
            results["success"].append(result)
            logger.info("✅ {} - {} chunks created", file_path.name, result.get("chunks_created", 0))
        else:
            results["skipped"].append(result)
    
    return results


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Batch upload documents to ARES")
    parser.add_argument(
        "directory",
        type=Path,
        help="Directory containing documents to upload",
    )
    parser.add_argument(
        "--api-url",
        type=str,
        default="http://localhost:8000",
        help="ARES API URL (default: http://localhost:8000)",
    )
    parser.add_argument(
        "--extensions",
        nargs="+",
        default=["pdf", "docx", "txt", "md", "xlsx"],
        help="File extensions to process (default: pdf docx txt md xlsx)",
    )
    
    args = parser.parse_args()
    
    if not args.directory.exists():
        logger.error("Directory does not exist: {}", args.directory)
        sys.exit(1)
    
    if not args.directory.is_dir():
        logger.error("Not a directory: {}", args.directory)
        sys.exit(1)
    
    print("🛡️ ARES - Batch Document Upload")
    print("=" * 40)
    print(f"Directory: {args.directory}")
    print(f"API URL: {args.api_url}")
    print(f"Extensions: {', '.join(args.extensions)}")
    print()
    
    results = batch_upload(args.directory, args.api_url, args.extensions)
    
    print()
    print("=" * 40)
    print("Upload Summary:")
    print(f"  ✅ Success: {len(results['success'])}")
    print(f"  ❌ Failed: {len(results['failed'])}")
    print(f"  ⏭️  Skipped: {len(results['skipped'])}")
    
    if results["failed"]:
        print("\nFailed uploads:")
        for item in results["failed"]:
            print(f"  - {item.get('filename', 'Unknown')}: {item.get('error', 'Unknown error')}")
    
    sys.exit(0 if not results["failed"] else 1)


if __name__ == "__main__":
    main()
