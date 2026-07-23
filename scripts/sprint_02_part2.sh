#!/usr/bin/env bash

###############################################################################
# Atmospheric Complexity Framework
# Sprint 02 - Part 2
# Utils Module
###############################################################################

set -e

PROJECT="/home/souhaib/ACF"

echo "=========================================="
echo "ACF - Sprint 02 - Part 2"
echo "Utils Module"
echo "=========================================="

cd "$PROJECT"

mkdir -p src/acf/utils

###############################################################################
# __init__.py
###############################################################################

cat > src/acf/utils/__init__.py << 'EOPY'
"""
Utility package for ACF.
"""
EOPY

###############################################################################
# paths.py
###############################################################################

cat > src/acf/utils/paths.py << 'EOPY'
"""
Project path utilities.
"""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]

CONFIG = ROOT / "config"
LOGS = ROOT / "logs"
CACHE = ROOT / "cache"
WORKSPACE = ROOT / "workspace"
PLUGINS = ROOT / "plugins"
EXPORTS = ROOT / "exports"
IMPORTS = ROOT / "imports"
TEMP = ROOT / "temp"
EOPY

###############################################################################
# files.py
###############################################################################

cat > src/acf/utils/files.py << 'EOPY'
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
EOPY

###############################################################################
# validators.py
###############################################################################

cat > src/acf/utils/validators.py << 'EOPY'
"""
Validation helpers.
"""

from pathlib import Path


def is_existing_file(filename):
    return Path(filename).is_file()


def is_existing_directory(dirname):
    return Path(dirname).is_dir()
EOPY

###############################################################################
# time.py
###############################################################################

cat > src/acf/utils/time.py << 'EOPY'
"""
Time utilities.
"""

from datetime import datetime


def now():
    return datetime.now()


def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
EOPY

echo ""
echo "Utils module created successfully."
