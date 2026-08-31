"""
Atmospheric Complexity Framework (ACF)

HPC CONNECTOR - Output & Artifact Manager (ACF-HPC-004)

Organizes forecast outputs, logs, checkpoints, restart files, and generates JSON summaries.
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class HPCOutputManager:
    """
    Manages hierarchical NWP output structures and JSON metadata.
    """

    def __init__(self, base_dir: str = "/tmp/acf_outputs") -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def initialize_run_directory(self, run_id: str) -> dict[str, str]:
        """
        Creates structured directory hierarchy for a specific run ID:
        outputs/, logs/, checkpoints/, restart/, forecasts/.
        """
        run_dir = self.base_dir / run_id

        subdirs = {
            "root": str(run_dir),
            "outputs": str(run_dir / "outputs"),
            "logs": str(run_dir / "logs"),
            "checkpoints": str(run_dir / "checkpoints"),
            "restart": str(run_dir / "restart"),
            "forecasts": str(run_dir / "forecasts"),
        }

        for path_str in subdirs.values():
            Path(path_str).mkdir(parents=True, exist_ok=True)

        logger.info(f"Initialized output structure in {run_dir}")
        return subdirs

    def save_metadata(self, run_id: str, metadata: dict[str, Any]) -> str:
        """
        Generates and saves a JSON summary file for the run.
        """
        subdirs = self.initialize_run_directory(run_id)
        meta_file = Path(subdirs["root"]) / "run_summary.json"

        payload = {
            "run_id": run_id,
            "timestamp": time.time(),
            "iso_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "subdirectories": subdirs,
            "metadata": metadata,
        }

        meta_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return str(meta_file)

    def list_run_files(self, run_id: str, category: str = "forecasts") -> list[str]:
        """
        Lists files stored in a specific output category.
        """
        run_dir = self.base_dir / run_id / category
        if not run_dir.exists():
            return []
        return [str(p) for p in run_dir.iterdir() if p.is_file()]
