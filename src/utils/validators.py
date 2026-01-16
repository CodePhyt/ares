"""
Validation utilities for ARES.
"""

from typing import Optional, List
from pathlib import Path
from loguru import logger


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """
    Validate file extension.

    Args:
        filename: Name of the file
        allowed_extensions: List of allowed extensions (without dot)

    Returns:
        True if extension is allowed
    """
    if not filename:
        return False
    
    extension = Path(filename).suffix.lower().lstrip(".")
    return extension in [ext.lower() for ext in allowed_extensions]


def parse_size(size_str: str) -> int:
    """
    Parse size string (e.g., "100MB") to bytes.

    Args:
        size_str: Size string like "100MB", "2GB"

    Returns:
        Size in bytes
    """
    size_str = size_str.upper().strip()
    
    if size_str.endswith("KB"):
        return int(size_str[:-2]) * 1024
    elif size_str.endswith("MB"):
        return int(size_str[:-2]) * 1024 * 1024
    elif size_str.endswith("GB"):
        return int(size_str[:-2]) * 1024 * 1024 * 1024
    elif size_str.endswith("TB"):
        return int(size_str[:-2]) * 1024 * 1024 * 1024 * 1024
    else:
        # Assume bytes if no unit
        try:
            return int(size_str)
        except ValueError:
            logger.warning("Could not parse size string: {}, defaulting to 100MB", size_str)
            return 100 * 1024 * 1024


def validate_query_length(query: str, max_length: int = 10000) -> tuple[bool, Optional[str]]:
    """
    Validate query length.

    Args:
        query: Query string
        max_length: Maximum allowed length

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not query or not query.strip():
        return False, "Query cannot be empty"
    
    if len(query) > max_length:
        return False, f"Query too long. Maximum length: {max_length} characters"
    
    return True, None
