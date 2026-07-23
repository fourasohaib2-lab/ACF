#!/usr/bin/env bash

###############################################################################
# Atmospheric Complexity Framework
# Sprint 02 - Part 3
# Unit Tests
###############################################################################

set -e

PROJECT="/home/souhaib/ACF"

echo "=============================================="
echo " ACF - Sprint 02 - Part 3"
echo " Unit Tests"
echo "=============================================="

cd "$PROJECT"

mkdir -p tests

###############################################################################
# __init__.py
###############################################################################

touch tests/__init__.py

###############################################################################
# test_version.py
###############################################################################

cat > tests/test_version.py << 'EOPY'
from acf.core.version import __version__

def test_version():
    assert __version__ == "0.1.0"
EOPY

###############################################################################
# test_metadata.py
###############################################################################

cat > tests/test_metadata.py << 'EOPY'
from acf.core.metadata import PROJECT_NAME

def test_project_name():
    assert PROJECT_NAME == "Atmospheric Complexity Framework"
EOPY

###############################################################################
# test_constants.py
###############################################################################

cat > tests/test_constants.py << 'EOPY'
from acf.core.constants import APP_NAME

def test_app_name():
    assert APP_NAME == "ACF"
EOPY

###############################################################################
# test_environment.py
###############################################################################

cat > tests/test_environment.py << 'EOPY'
from acf.core.environment import operating_system

def test_operating_system():
    assert isinstance(operating_system(), str)
EOPY

###############################################################################
# test_utils.py
###############################################################################

cat > tests/test_utils.py << 'EOPY'
from acf.utils.files import ensure_directory
from pathlib import Path

def test_create_directory(tmp_path):
    directory = tmp_path / "demo"
    ensure_directory(directory)
    assert Path(directory).exists()
EOPY

echo ""
echo "=============================================="
echo "Tests created successfully."
echo "=============================================="
