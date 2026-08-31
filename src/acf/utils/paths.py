"""
Project path utilities.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

CONFIG = ROOT / "config"
LOGS = ROOT / "logs"
CACHE = ROOT / "cache"
WORKSPACE = ROOT / "workspace"
PLUGINS = ROOT / "plugins"
EXPORTS = ROOT / "exports"
IMPORTS = ROOT / "imports"
TEMP = ROOT / "temp"
