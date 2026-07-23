#!/usr/bin/env bash

set -e

PROJECT="/home/souhaib/ACF"

echo "======================================="
echo " ACF Sprint 06 - Part 8"
echo " Packaging"
echo "======================================="

####################################################
# pyproject.toml
####################################################

cat > "$PROJECT/pyproject.toml" << 'EOF'
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "acf"
version = "0.1.0"
description = "Atmospheric Complexity Framework"
readme = "README.md"
requires-python = ">=3.12"

authors = [
    {name="Sohaib Foura"}
]

dependencies = [
    "numpy",
    "scipy",
    "pandas",
    "xarray",
    "netCDF4",
    "cfgrib",
    "eccodes",
    "matplotlib",
    "cartopy",
    "pyproj",
    "shapely",
    "rasterio",
    "h5py",
    "PySide6",
]

[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
EOF

####################################################
# requirements.txt
####################################################

cat > "$PROJECT/requirements.txt" << 'EOF'
numpy
scipy
pandas
xarray
netCDF4
cfgrib
eccodes
matplotlib
cartopy
pyproj
shapely
rasterio
h5py
PySide6
EOF

####################################################
# requirements-dev.txt
####################################################

cat > "$PROJECT/requirements-dev.txt" << 'EOF'
-r requirements.txt

pytest
pytest-cov
black
ruff
mypy
EOF

####################################################
# Makefile
####################################################

cat > "$PROJECT/Makefile" << 'EOF'
install:
	pip install -e .

dev:
	pip install -r requirements-dev.txt

test:
	PYTHONPATH=src pytest -v

format:
	black src tests

lint:
	ruff check src tests

typecheck:
	mypy src

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -name "*.pyc" -delete
EOF

echo
echo "Packaging successfully configured."

