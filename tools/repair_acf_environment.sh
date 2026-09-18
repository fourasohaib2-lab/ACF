#!/bin/bash
set -uo pipefail

echo "======================================"
echo " ACF - ENVIRONMENT REPAIR SCRIPT"
echo " Atmospheric Complexity Framework"
echo "======================================"

# Résolu par rapport à l'emplacement du script lui-même, pas par rapport à
# $HOME/ACF : cette hypothèse est fausse dès que le dépôt n'est pas cloné
# exactement dans le home de l'utilisateur (ex. $HOME=/root mais dépôt dans
# /home/user/ACF) - repro confirmée sur cette machine, où l'ancienne version
# échouait immédiatement à l'étape [1/10] "dossier src/acf introuvable".
# tools/agy_acf_full_repair.sh utilise déjà ce pattern robuste ; on
# l'aligne ici.
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$PROJECT_DIR" || exit 1


echo ""
echo "[1/10] Vérification du projet..."

if ! ls src/acf >/dev/null 2>&1; then
    echo "ERREUR: dossier src/acf introuvable"
    exit 1
fi


echo ""
echo "[2/10] Sélection d'un interpréteur Python >= 3.12..."

# pyproject.toml déclare requires-python = ">=3.12". Utiliser simplement
# "python3" du PATH est incorrect : sur une machine où "python3" pointe
# vers une version antérieure (ex. 3.11, comme sur cette machine alors que
# python3.12/3.13 sont aussi installés), `pip install -e .` échoue
# immédiatement avec "Package 'acf' requires a different Python" - repro
# confirmée. On cherche donc explicitement un interpréteur compatible.
PYTHON_BIN=""
for _cand in python3.13 python3.12 python3 python; do
    if command -v "$_cand" >/dev/null 2>&1 && \
       "$_cand" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)' 2>/dev/null; then
        PYTHON_BIN="$_cand"
        break
    fi
done

if [ -z "$PYTHON_BIN" ]; then
    echo "ERREUR: aucun interpréteur Python >= 3.12 trouvé dans le PATH"
    echo "        (requis par pyproject.toml: requires-python = \">=3.12\")."
    exit 1
fi

echo "Interpréteur retenu: $PYTHON_BIN ($("$PYTHON_BIN" --version 2>&1))"


echo ""
echo "[3/10] Activation environnement virtuel..."

if [ -d ".venv" ]; then
    if .venv/bin/python -c 'import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)' 2>/dev/null; then
        # shellcheck disable=SC1091
        source .venv/bin/activate
    else
        echo ".venv existant incompatible ($(.venv/bin/python --version 2>&1), < 3.12 requis), recréation..."
        rm -rf .venv
        "$PYTHON_BIN" -m venv .venv || exit 1
        # shellcheck disable=SC1091
        source .venv/bin/activate
    fi
else
    echo "Création du venv..."
    "$PYTHON_BIN" -m venv .venv || exit 1
    # shellcheck disable=SC1091
    source .venv/bin/activate
fi

STATUS=0


echo ""
echo "[4/10] Mise à jour pip..."

python -m pip install --upgrade pip setuptools wheel || STATUS=1


echo ""
echo "[5/10] Installation du projet ACF (dépendances déclarées dans pyproject.toml)..."

# On installe le projet en mode éditable plutôt que de dupliquer la liste des
# dépendances ici : ça évite que ce script diverge de pyproject.toml (il
# manquait rasterio/h5py et installait PyQt6+shiboken6, qui ne sont pas des
# dépendances du projet - seul PySide6 est utilisé, et avoir les deux
# bindings Qt installés en même temps peut provoquer des conflits).
pip install -U -e . || STATUS=1


echo ""
echo "[6/10] Installation dépendances de développement/test..."

# Utilise l'extra "dev" de pyproject.toml (pytest, pytest-cov,
# pytest-timeout, black, ruff, mypy) plutôt qu'une liste ad hoc : ruff et
# mypy y sont notamment utiles à tools/agy_acf_full_repair.sh, dont
# run_ruff()/le "P2" de son prompt AGY supposent ces outils disponibles
# dans le venv du projet - sans ça il se contente d'un WARN silencieux et
# ne valide jamais rien. pytest-qt n'est déclaré ni dans pyproject.toml ni
# dans requirements-dev.txt alors que de nombreux tests GUI (tests/gui/*,
# tests/test_awci_*, tests/test_map_*...) utilisent la fixture `qtbot` -
# installé explicitement en plus de l'extra "dev".
pip install -U -e ".[dev]" pytest-qt || STATUS=1


echo ""
echo "[7/10] Installation des extras optionnels (extra \"all\" de pyproject.toml)..."

# Remplace l'ancienne liste ad hoc "metpy geopandas shapely pyproj" par
# l'extra "all" réellement déclaré dans pyproject.toml (= tout le
# requirements.txt) :
# - geopandas et shapely ne sont importés nulle part dans src/ ou tests/
#   (dépendances mortes, exactement comme celles déjà retirées de
#   pyproject.toml/requirements.txt le 2026-09-02 - cf. leurs commentaires)
#   donc les installer ici n'apportait rien.
# - à l'inverse, PySide6/matplotlib (extra "gui"), cartopy (extra
#   "geospatial") et xarray/netCDF4 (extra "formats") n'étaient JAMAIS
#   installés par ce script alors que l'étape [8/10] ci-dessous vérifie
#   justement ces imports : la vérification échouait donc
#   systématiquement, même après une installation par ailleurs réussie.
# - repro allée plus loin que le seul step 8 : avec seulement
#   gui+geospatial+formats+science+hpc installés, `pytest -v` à
#   l'étape [10/10] échoue quand même dès la collecte sur
#   tests/test_fno_surrogate.py ("No module named 'torch'", extra "ai")
#   et tests/test_web_*.py ("No module named 'fastapi'", extra "web") -
#   donc rien de moins que "all" ne fait réellement passer toute la
#   suite (l'objectif affiché de ce script), et pyproject.toml le
#   déclare déjà tout prêt pour ça.
pip install -U -e ".[all]" || STATUS=1


echo ""
echo "[8/10] Vérification imports Python..."

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
echo "[9/10] Nettoyage cache pytest..."

rm -rf .pytest_cache
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null


echo ""
echo "[10/10] Lancement tests ACF..."

export PYTHONPATH=src

# Sans serveur d'affichage (CI/sandbox headless - repro sur cette machine :
# DISPLAY vide), pytest-qt plante dès pytest_configure() en essayant de
# charger QtGui avec la plateforme Qt par défaut ("xcb", qui a besoin d'un
# vrai X server). On force donc le backend offscreen de Qt dans ce cas
# précis uniquement, sans changer le comportement sur un poste de
# développement avec un vrai DISPLAY (ou une valeur QT_QPA_PLATFORM déjà
# choisie explicitement par l'utilisateur).
if [ -z "${DISPLAY:-}" ] && [ -z "${QT_QPA_PLATFORM:-}" ]; then
    echo "Aucun DISPLAY détecté : QT_QPA_PLATFORM=offscreen"
    export QT_QPA_PLATFORM=offscreen
fi

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
