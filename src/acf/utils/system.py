"""
Atmospheric Complexity Framework (ACF)
System Utilities
"""

import platform
from pathlib import Path


def get_os_name() -> str:
    """Return the operating system name."""
    return platform.system()


def get_python_version() -> str:
    """Return the current Python version."""
    return platform.python_version()


def get_project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).resolve().parents[3]
