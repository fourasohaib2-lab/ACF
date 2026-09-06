#!/usr/bin/env bash
# ACF — Installation complète des dépendances (système + Python)
#
# Couvre : les dépendances cœur, TOUS les extras pyproject.toml ([all]),
# les outils dev ([dev]), et les bibliothèques système natives requises
# pour que cfgrib/eccodes/netCDF4/pyproj/cartopy/PySide6 fonctionnent
# réellement (pas juste s'installer).
#
# Usage :
#   cd /chemin/vers/ACF
#   bash install_all_deps.sh
#
# Options :
#   SKIP_APT=1   ./install_all_deps.sh   # saute l'installation système (déjà fait / pas de sudo)
#   SKIP_TESTS=1 ./install_all_deps.sh   # saute la suite de tests finale
#
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"

if [ ! -f "pyproject.toml" ]; then
  echo "ERREUR : pyproject.toml introuvable dans $REPO_ROOT" >&2
  echo "Lancez ce script depuis la racine du dépôt ACF." >&2
  exit 1
fi

echo "=== ACF — installation complète ==="
echo "Dépôt : $REPO_ROOT"
echo ""

# ---------------------------------------------------------------------------
# 1. Dépendances système (bibliothèques C/Fortran natives)
# ---------------------------------------------------------------------------
if [ "${SKIP_APT:-0}" != "1" ]; then
  if command -v apt-get >/dev/null 2>&1; then
    echo "--- [1/4] Dépendances système (apt) ---"
    SUDO=""
    if [ "$(id -u)" != "0" ]; then
      command -v sudo >/dev/null 2>&1 && SUDO="sudo"
    fi
    $SUDO apt-get update -y
    $SUDO apt-get install -y \
      python3.12 python3.12-venv python3.12-dev \
      build-essential \
      libeccodes-dev libnetcdf-dev \
      libproj-dev libgeos-dev proj-bin \
      libopenmpi-dev openmpi-bin \
      libgl1 libxkbcommon-x11-0 libegl1 \
      pkg-config
  else
    echo "--- [1/4] apt-get introuvable (pas Debian/Ubuntu) ---"
    echo "Installez manuellement l'équivalent de : eccodes, netcdf, proj, geos, openmpi, Qt/OpenGL runtime."
    echo "  - macOS (Homebrew) : brew install eccodes netcdf proj geos open-mpi"
    echo "  - Windows : privilégier les wheels binaires pip (voir étape 3) ; PySide6/cartopy embarquent déjà leurs libs."
  fi
else
  echo "--- [1/4] Dépendances système : SAUTÉ (SKIP_APT=1) ---"
fi
echo ""

# ---------------------------------------------------------------------------
# 2. Environnement virtuel Python 3.12+
# ---------------------------------------------------------------------------
echo "--- [2/4] Environnement virtuel (.venv, Python 3.12+) ---"
PYBIN=""
for cand in python3.13 python3.12; do
  if command -v "$cand" >/dev/null 2>&1; then PYBIN="$cand"; break; fi
done
if [ -z "$PYBIN" ]; then
  echo "ERREUR : aucun interpréteur Python >=3.12 trouvé (requis par pyproject.toml)." >&2
  echo "Installez Python 3.12+ avant de continuer." >&2
  exit 1
fi
echo "Interpréteur retenu : $($PYBIN --version)"

if [ ! -d ".venv" ]; then
  "$PYBIN" -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
echo ""

# ---------------------------------------------------------------------------
# 3. Dépendances Python — cœur + TOUS les extras + outils dev
# ---------------------------------------------------------------------------
echo "--- [3/4] Dépendances Python (extras [all,dev]) ---"
pip install -e ".[all,dev]"
echo ""

echo "Vérification par import réel (pas juste 'pip install' silencieux) :"
python - <<'PY'
mods = [
    "numpy", "scipy", "yaml", "loguru",
    "PySide6", "matplotlib",
    "cartopy", "pyproj",
    "xarray", "netCDF4", "cfgrib", "eccodes", "epygram", "zarr",
    "metpy",
    "paramiko",
    "fastapi", "uvicorn", "websockets", "httpx",
    "torch",
    "psutil",
    "pytest",
]
missing = []
for m in mods:
    try:
        __import__(m)
        print(f"  OK      {m}")
    except Exception as e:
        missing.append(m)
        print(f"  MANQUANT {m}: {e}")
if missing:
    print(f"\n{len(missing)} module(s) toujours manquant(s) après installation : {missing}")
else:
    print("\nTous les modules s'importent réellement.")
PY
echo ""

# ---------------------------------------------------------------------------
# 4. Suite de tests complète (validation réelle, pas juste l'installation)
# ---------------------------------------------------------------------------
if [ "${SKIP_TESTS:-0}" != "1" ]; then
  echo "--- [4/4] Suite de tests complète (pytest) ---"
  pytest -q || {
    echo ""
    echo "Des tests échouent — voir la sortie ci-dessus. L'installation des paquets"
    echo "est terminée ; les échecs restants sont des bugs de code, pas des paquets"
    echo "manquants (relancez avec SKIP_TESTS=1 pour ignorer cette étape)."
    exit 1
  }
else
  echo "--- [4/4] Suite de tests : SAUTÉ (SKIP_TESTS=1) ---"
fi

echo ""
echo "=== Terminé. Activez l'environnement avec : source .venv/bin/activate ==="
