"""
File utilities.
"""

from pathlib import Path


def ensure_directory(path):
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def file_exists(path):
    return Path(path).exists()
