"""
Validation helpers.
"""

from pathlib import Path


def is_existing_file(filename):
    return Path(filename).is_file()


def is_existing_directory(dirname):
    return Path(dirname).is_dir()
