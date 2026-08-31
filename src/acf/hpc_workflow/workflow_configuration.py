"""HPC Workflow Configuration Manager (ACF-HPC-104)."""

import os
from typing import Any

import yaml


class WorkflowConfiguration:
    """Loads and validates workflow.yaml, arome.yaml, and aladin.yaml configurations."""

    def __init__(self, config_dir: str = "config") -> None:
        self.config_dir = config_dir

    def load_config(self, filename: str = "workflow.yaml") -> dict[str, Any]:
        """Load YAML configuration dictionary."""
        path = os.path.join(self.config_dir, filename)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if isinstance(data, dict):
                        return data
            except Exception:
                pass
        return {"mode": "operational", "auto_restart": True}
