#!/usr/bin/env bash

set -e

PROJECT="/home/souhaib/ACF"

echo "========================================"
echo " ACF - Sprint 03 - Part 1"
echo " Desktop Framework"
echo "========================================"

cd "$PROJECT"

echo "[1/8] Création des dossiers..."

mkdir -p src/acf/gui
mkdir -p src/acf/gui/widgets
mkdir -p src/acf/gui/dialogs
mkdir -p src/acf/gui/resources/icons
mkdir -p src/acf/gui/resources/images
mkdir -p src/acf/gui/resources/themes

echo "[2/8] Création des fichiers..."

touch src/acf/gui/__init__.py
touch src/acf/gui/app.py
touch src/acf/gui/main_window.py
touch src/acf/gui/menu.py
touch src/acf/gui/toolbar.py
touch src/acf/gui/statusbar.py
touch src/acf/gui/theme.py
touch src/acf/gui/splash.py

touch src/acf/gui/widgets/__init__.py
touch src/acf/gui/widgets/console.py
touch src/acf/gui/widgets/explorer.py
touch src/acf/gui/widgets/property_panel.py
touch src/acf/gui/widgets/map_view.py

touch src/acf/gui/dialogs/__init__.py

echo "[3/8] Structure créée."

echo
echo "GUI prête pour le développement."
