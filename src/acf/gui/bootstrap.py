"""Runtime Bootstrap & Environment Configurator for ACF GUI Application (ACF-BOOT-001).

Configures PYTHONPATH, Qt QPA Platform backends (VNC/X11/Wayland), and HPC detection automatically.
"""

from __future__ import annotations

import logging
import os
import socket
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger("acf.gui.bootstrap")


def _detect_project_root() -> Path:
    """Detect git repository root directory or fallback to parent paths."""
    try:
        res = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        root = Path(res.stdout.strip())
        if root.exists():
            return root
    except Exception:
        pass

    # Fallback to traversing parent directories from bootstrap.py
    current = Path(__file__).resolve().parent
    for parent in [current] + list(current.parents):
        if (parent / "src" / "acf").exists() or (parent / ".git").exists():
            return parent

    return Path.cwd()


def _is_hpc_environment() -> bool:
    """Detect if executing on an HPC node or cluster login node."""
    hpc_indicators = ["SLURM_JOB_ID", "PBS_JOBID", "LSB_JOBID", "ENVIRONMENT"]
    if any(k in os.environ for k in hpc_indicators):
        return True

    hostname = socket.gethostname().lower()
    hpc_host_keywords = ["sms", "fennec", "node", "hpc", "cluster", "login", "compute"]
    return any(kw in hostname for kw in hpc_host_keywords)


def configure_runtime() -> Path:
    """Configure runtime environment, PYTHONPATH, and Qt QPA platform backends.

    Returns:
        Path: Resolved project root directory.
    """
    # 1. Logging Setup
    if not logger.handlers:
        logging.basicConfig(
            level=logging.INFO,
            format="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%H:%M:%S",
        )

    # 2. Detect Project Root & Configure PYTHONPATH
    project_root = _detect_project_root()
    src_dir = project_root / "src"

    if src_dir.exists():
        src_str = str(src_dir.resolve())
        if src_str not in sys.path:
            sys.path.insert(0, src_str)

        curr_pythonpath = os.environ.get("PYTHONPATH", "")
        if src_str not in curr_pythonpath.split(os.pathsep):
            os.environ["PYTHONPATH"] = f"{src_str}{os.pathsep}{curr_pythonpath}".strip(os.pathsep)

    logger.info(f"Project root detected: {project_root}")

    # 3. Detect Execution Host (HPC vs Workstation)
    is_hpc = _is_hpc_environment()
    env_type = "HPC Cluster Node" if is_hpc else "Workstation / Local PC"
    logger.info(f"Running on: {env_type} ({socket.gethostname()})")

    # 4. Detect & Configure Qt QPA Platform Backend
    display = os.environ.get("DISPLAY", "").strip()
    wayland_display = os.environ.get("WAYLAND_DISPLAY", "").strip()
    qpa_platform = os.environ.get("QT_QPA_PLATFORM", "").strip()

    if not qpa_platform:
        if not display and not wayland_display:
            # Headless environment: Auto-configure Qt VNC platform
            auto_vnc = "vnc:size=1280x720:port=5910"
            os.environ["QT_QPA_PLATFORM"] = auto_vnc
            logger.info(f"DISPLAY unavailable. Auto-configured Qt QPA Platform: {auto_vnc}")
        elif wayland_display:
            logger.info("DISPLAY detected: Using Wayland backend")
        else:
            logger.info(f"DISPLAY detected ({display}): Using X11 backend")
    else:
        logger.info(f"Using explicitly configured Qt QPA Platform: {qpa_platform}")

    return project_root
