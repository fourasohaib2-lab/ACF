#!/usr/bin/env bash

set -e

PROJECT="/home/souhaib/ACF"

echo "=========================================="
echo "ACF Sprint 05 - Dashboard Engine"
echo "Part 1"
echo "=========================================="

cd "$PROJECT"

mkdir -p src/acf/dashboard/panels

touch src/acf/dashboard/__init__.py
touch src/acf/dashboard/dashboard.py
touch src/acf/dashboard/layout.py
touch src/acf/dashboard/manager.py
touch src/acf/dashboard/widgets.py

touch src/acf/dashboard/panels/__init__.py
touch src/acf/dashboard/panels/map_panel.py
touch src/acf/dashboard/panels/chart_panel.py
touch src/acf/dashboard/panels/explorer_panel.py
touch src/acf/dashboard/panels/property_panel.py
touch src/acf/dashboard/panels/timeline_panel.py
touch src/acf/dashboard/panels/status_panel.py

echo
echo "Dashboard Engine created successfully."
