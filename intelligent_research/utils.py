"""
Shared utility functions for intelligent research system.

This module provides common helper functions used across the system.
"""

import re
import os
from pathlib import Path


def load_env_file(env_path: str = None) -> None:
    """
    Load environment variables from .env file if it exists.

    Args:
        env_path: Optional path to .env file. If None, looks in parent directory.
    """
    if env_path is None:
        env_path = Path(__file__).parent.parent / '.env'
    else:
        env_path = Path(env_path)

    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Only set if not already in environment
                    if key not in os.environ:
                        os.environ[key] = value.strip()


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a string to be safe for use as a filename or directory name.

    Args:
        filename: String to sanitize

    Returns:
        Sanitized string safe for filesystem use
    """
    # Remove non-alphanumeric characters except spaces and hyphens
    sanitized = re.sub(r'[^\w\s-]', '', filename)
    # Replace spaces with underscores
    sanitized = re.sub(r'\s+', '_', sanitized)
    # Remove leading/trailing underscores
    return sanitized.strip('_')


def validate_url(url: str) -> bool:
    """
    Basic URL validation.

    Args:
        url: URL string to validate

    Returns:
        True if URL appears valid
    """
    if not url:
        return False

    # Basic URL pattern check
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return bool(url_pattern.match(url))


def truncate_string(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate a string to a maximum length.

    Args:
        text: String to truncate
        max_length: Maximum length before truncation
        suffix: Suffix to add when truncated

    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix
