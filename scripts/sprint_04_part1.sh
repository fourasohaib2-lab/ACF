#!/usr/bin/env bash

set -e

PROJECT="/home/souhaib/ACF"

echo "==============================================="
echo "      ACF Sprint 04 - Workspace Manager"
echo "==============================================="

cd "$PROJECT"

mkdir -p src/acf/workspace

touch src/acf/workspace/__init__.py
touch src/acf/workspace/project.py
touch src/acf/workspace/manager.py
touch src/acf/workspace/serializer.py
touch src/acf/workspace/templates.py
touch src/acf/workspace/metadata.py
touch src/acf/workspace/exceptions.py

echo
echo "Workspace module created."
