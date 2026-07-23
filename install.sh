#!/usr/bin/env bash

###############################################################################
# Atmospheric Complexity Framework (ACF)
# Installation Script
###############################################################################

set -e

echo "==========================================="
echo " Atmospheric Complexity Framework (ACF)"
echo " Installer v0.1"
echo "==========================================="

# Vérification Python
if ! command -v python3 >/dev/null 2>&1; then
    echo "Python3 n'est pas installé."
    exit 1
fi

# Création du venv
if [ ! -d ".venv" ]; then
    echo "Création de l'environnement virtuel..."
    python3 -m venv .venv
fi

# Activation
source .venv/bin/activate

echo "Mise à jour de pip..."
python -m pip install --upgrade pip setuptools wheel

echo "Installation des dépendances..."
pip install -e .

echo ""
echo "==========================================="
echo " Installation terminée avec succès !"
echo "==========================================="
echo ""
echo "Pour lancer ACF :"
echo ""
echo "source .venv/bin/activate"
echo "python -m acf.main"
