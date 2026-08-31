"""
Environment information.
"""

import pathlib
import platform


def operating_system():
    return platform.system()


def python_version():
    return platform.python_version()


def project_root():
    return pathlib.Path(__file__).resolve().parents[3]
