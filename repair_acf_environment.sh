#!/bin/bash
set -uo pipefail

echo "======================================"
echo " ACF - ENVIRONMENT REPAIR SCRIPT"
echo " Atmospheric Complexity Framework"
echo "======================================"

PROJECT_DIR="$HOME/ACF"

cd "$PROJECT_DIR" || exit 1


echo ""
echo "[1/9] Vérification du projet..."

if ! ls src/acf >/dev/null 2>&1; then
    echo "ERREUR: dossier src/acf introuvable"
    exit 1
fi


echo ""
echo "[2/9] Activation environnement virtuel..."

if [ -d ".venv" ]; then
    # shellcheck disable=SC1091
    source .venv/bin/activate
else
    echo "Création du venv..."
    python3 -m venv .venv || exit 1
    # shellcheck disable=SC1091
    source .venv/bin/activate
fi

STATUS=0


echo ""
echo "[3/9] Mise à jour pip..."

python -m pip install --upgrade pip setuptools wheel || STATUS=1


echo ""
echo "[4/9] Installation du projet ACF (dépendances déclarées dans pyproject.toml)..."

# On installe le projet en mode éditable plutôt que de dupliquer la liste des
# dépendances ici : ça évite que ce script diverge de pyproject.toml (il
# manquait rasterio/h5py et installait PyQt6+shiboken6, qui ne sont pas des
# dépendances du projet - seul PySide6 est utilisé, et avoir les deux
# bindings Qt installés en même temps peut provoquer des conflits).
pip install -U -e . || STATUS=1


echo ""
echo "[5/9] Installation dépendances de test..."

pip install -U \
    pytest \
    pytest-qt || STATUS=1


echo ""
echo "[6/9] Installation dépendances météo optionnelles..."

pip install -U \
    metpy \
    geopandas \
    shapely \
    pyproj || STATUS=1


echo ""
echo "[7/9] Vérification imports Python..."

python <<EOF
modules = [
    "PySide6",
    "matplotlib",
    "cartopy",
    "xarray",
    "netCDF4",
    "metpy",
    "acf",
]

failed = False
for m in modules:
    try:
        __import__(m)
        print("OK :", m)
    except Exception as e:
        print("FAIL :", m, e)
        failed = True

raise SystemExit(1 if failed else 0)
EOF
[ $? -eq 0 ] || STATUS=1


echo ""
echo "[8/9] Nettoyage cache pytest..."

rm -rf .pytest_cache
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null


echo ""
echo "[9/9] Lancement tests ACF..."

export PYTHONPATH=src

if ! pytest -v; then
    STATUS=1
fi


echo ""
echo "======================================"
if [ "$STATUS" -eq 0 ]; then
    echo " REPARATION TERMINEE AVEC SUCCES"
    echo "======================================"
    exit 0
else
    echo " REPARATION INCOMPLETE"
    echo " Au moins une étape a échoué (voir ci-dessus)."
    echo "======================================"
    exit 1
fi
