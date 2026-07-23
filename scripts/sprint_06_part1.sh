#!/usr/bin/env bash

set -e

PROJECT="/home/souhaib/ACF"

echo "======================================="
echo " ACF Sprint 06 - Scientific Data Engine"
echo " Part 1 : Architecture"
echo "======================================="

mkdir -p "$PROJECT/src/acf/data"

touch "$PROJECT/src/acf/data/__init__.py"

touch "$PROJECT/src/acf/data/dataset.py"
touch "$PROJECT/src/acf/data/manager.py"
touch "$PROJECT/src/acf/data/factory.py"

mkdir -p "$PROJECT/src/acf/data/readers"

touch "$PROJECT/src/acf/data/readers/__init__.py"
touch "$PROJECT/src/acf/data/readers/netcdf_reader.py"
touch "$PROJECT/src/acf/data/readers/grib_reader.py"
touch "$PROJECT/src/acf/data/readers/geotiff_reader.py"
touch "$PROJECT/src/acf/data/readers/csv_reader.py"
touch "$PROJECT/src/acf/data/readers/json_reader.py"

mkdir -p "$PROJECT/src/acf/data/writers"

touch "$PROJECT/src/acf/data/writers/__init__.py"
touch "$PROJECT/src/acf/data/writers/netcdf_writer.py"
touch "$PROJECT/src/acf/data/writers/csv_writer.py"

echo
echo "Scientific Data Engine created."

