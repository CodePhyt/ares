#!/usr/bin/env python3
"""
Cleanup utility for ARES - remove old files and optimize database.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import argparse

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger


def cleanup_uploads(max_age_days: int = 30) -> int:
    """Remove old uploaded files."""
    upload_dir = Path("./uploads")
    if not upload_dir.exists():
        return 0
    
    cutoff_date = datetime.now() - timedelta(days=max_age_days)
    removed = 0
    
    for file_path in upload_dir.iterdir():
        if file_path.is_file():
            file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            if file_mtime < cutoff_date:
                try:
                    file_path.unlink()
                    removed += 1
                    logger.info("Removed old file: {}", file_path.name)
                except Exception as e:
                    logger.error("Error removing {}: {}", file_path, e)
    
    return removed


def cleanup_logs(max_age_days: int = 7) -> int:
    """Remove old log files."""
    log_files = list(Path(".").glob("*.log"))
    cutoff_date = datetime.now() - timedelta(days=max_age_days)
    removed = 0
    
    for log_file in log_files:
        if log_file.is_file():
            file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            if file_mtime < cutoff_date:
                try:
                    log_file.unlink()
                    removed += 1
                    logger.info("Removed old log: {}", log_file.name)
                except Exception as e:
                    logger.error("Error removing {}: {}", log_file, e)
    
    return removed


def get_directory_size(directory: Path) -> int:
    """Get total size of directory in bytes."""
    total = 0
    try:
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                total += file_path.stat().st_size
    except Exception as e:
        logger.error("Error calculating size of {}: {}", directory, e)
    return total


def format_size(size_bytes: int) -> str:
    """Format bytes to human-readable size."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Cleanup ARES files and optimize storage")
    parser.add_argument(
        "--uploads-age",
        type=int,
        default=30,
        help="Remove uploads older than N days (default: 30)",
    )
    parser.add_argument(
        "--logs-age",
        type=int,
        default=7,
        help="Remove logs older than N days (default: 7)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be removed without actually removing",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show storage statistics",
    )
    
    args = parser.parse_args()
    
    print("🛡️ ARES - Cleanup Utility")
    print("=" * 40)
    
    if args.stats:
        print("\nStorage Statistics:")
        directories = {
            "Uploads": Path("./uploads"),
            "ChromaDB": Path("./chroma_db"),
            "Data": Path("./data"),
        }
        
        for name, path in directories.items():
            if path.exists():
                size = get_directory_size(path)
                file_count = len(list(path.rglob("*"))) if path.is_dir() else 0
                print(f"  {name}: {format_size(size)} ({file_count} files)")
            else:
                print(f"  {name}: Not found")
    
    if args.dry_run:
        print("\n🔍 Dry run mode - no files will be removed")
    
    print(f"\nCleanup settings:")
    print(f"  Uploads older than: {args.uploads_age} days")
    print(f"  Logs older than: {args.logs_age} days")
    print()
    
    if not args.dry_run:
        # Cleanup uploads
        removed_uploads = cleanup_uploads(args.uploads_age)
        print(f"✅ Removed {removed_uploads} old upload files")
        
        # Cleanup logs
        removed_logs = cleanup_logs(args.logs_age)
        print(f"✅ Removed {removed_logs} old log files")
        
        print("\n✅ Cleanup completed!")
    else:
        print("\n🔍 Dry run completed - use without --dry-run to perform cleanup")


if __name__ == "__main__":
    main()
