#!/bin/bash

echo "======================================"
echo " ACF - ENVIRONMENT REPAIR SCRIPT"
echo " Atmospheric Complexity Framework"
echo "======================================"

PROJECT_DIR="$HOME/ACF"

cd "$PROJECT_DIR" || exit 1


echo ""
echo "[1/10] Vérification du projet..."
ls src/acf >/dev/null 2>&1

if [ $? -ne 0 ]; then
    echo "ERREUR: dossier src/acf introuvable"
    exit 1
fi


echo ""
echo "[2/10] Activation environnement virtuel..."

if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "Création du venv..."
    python3 -m venv .venv
    source .venv/bin/activate
fi


echo ""
echo "[3/10] Mise à jour pip..."

python -m pip install --upgrade pip setuptools wheel


echo ""
echo "[4/10] Installation dépendances scientifiques..."

pip install -U \
numpy \
scipy \
pandas \
matplotlib \
xarray \
netCDF4 \
cartopy \
cfgrib \
eccodes


echo ""
echo "[5/10] Installation interface graphique Qt..."

pip install -U \
PySide6 \
PyQt6 \
shiboken6


echo ""
echo "[6/10] Installation tests..."

pip install -U \
pytest \
pytest-qt


echo ""
echo "[7/10] Installation dépendances météo..."

pip install -U \
metpy \
geopandas \
shapely \
pyproj


echo ""
echo "[8/10] Vérification imports Python..."

python <<EOF

modules=[
"PySide6",
"matplotlib",
"cartopy",
"xarray",
"netCDF4",
"metpy",
"acf"
]

for m in modules:
    try:
        __import__(m)
        print("OK :",m)
    except Exception as e:
        print("FAIL :",m,e)

EOF


echo ""
echo "[9/10] Nettoyage cache pytest..."

rm -rf .pytest_cache
find . -name "__pycache__" -type d -exec rm -rf {} +


echo ""
echo "[10/10] Lancement tests ACF..."

export PYTHONPATH=src

pytest -v


echo ""
echo "======================================"
echo " REPARATION TERMINEE"
echo "======================================"
