#!/usr/bin/env bash

###############################################################################
# Atmospheric Complexity Framework
# Sprint 02 - Part 1
# Core Framework
###############################################################################

set -e

PROJECT="/home/souhaib/ACF"

echo "=============================================="
echo " ACF - Sprint 02 - Part 1"
echo " Core Framework"
echo "=============================================="

cd "$PROJECT"

echo "[1/8] Creating directories..."

mkdir -p src/acf/core

echo "[2/8] Creating version.py..."

cat > src/acf/core/version.py << 'EOF'
"""
ACF Version
"""

__version__ = "0.1.0"
__author__ = "Sohaib Foura"
__license__ = "Apache-2.0"
EOF

echo "[3/8] Creating metadata.py..."

cat > src/acf/core/metadata.py << 'EOF'
"""
Project metadata.
"""

PROJECT_NAME = "Atmospheric Complexity Framework"
SHORT_NAME = "ACF"

DESCRIPTION = (
    "Open scientific platform for atmospheric sciences."
)
EOF

echo "[4/8] Creating constants.py..."

cat > src/acf/core/constants.py << 'EOF'
"""
Global constants.
"""

APP_NAME = "ACF"

CONFIG_DIRECTORY = "config"

PLUGIN_DIRECTORY = "plugins"

WORKSPACE_DIRECTORY = "workspace"

LOG_DIRECTORY = "logs"

CACHE_DIRECTORY = "cache"

EXPORT_DIRECTORY = "exports"

IMPORT_DIRECTORY = "imports"
EOF

echo "[5/8] Creating exceptions.py..."

cat > src/acf/core/exceptions.py << 'EOF'
"""
Project exceptions.
"""

class ACFError(Exception):
    """Base exception."""


class ConfigurationError(ACFError):
    """Configuration exception."""


class PluginError(ACFError):
    """Plugin exception."""


class WorkspaceError(ACFError):
    """Workspace exception."""
EOF

echo "[6/8] Creating environment.py..."

cat > src/acf/core/environment.py << 'EOF'
"""
Environment information.
"""

import platform
import pathlib


def operating_system():
    return platform.system()


def python_version():
    return platform.python_version()


def project_root():
    return pathlib.Path(__file__).resolve().parents[3]
EOF

echo "[7/8] Verifying files..."

ls src/acf/core

echo "[8/8] Sprint completed."

echo ""
echo "Core Framework created successfully."
