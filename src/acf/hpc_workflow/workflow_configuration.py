"""HPC Workflow Configuration Manager (ACF-HPC-104)."""

import logging
import os
from typing import Any

import yaml

logger = logging.getLogger("acf.hpc_workflow.workflow_configuration")

#: Real fallback only for the honest case of "no config file was ever
#: provided" - never silently substituted for a real file that exists
#: but failed to load/parse (see load_config()'s own NOTE).
_DEFAULT_CONFIG: dict[str, Any] = {"mode": "operational", "auto_restart": True}


class WorkflowConfiguration:
    """Loads and validates workflow.yaml, arome.yaml, and aladin.yaml configurations."""

    def __init__(self, config_dir: str = "config") -> None:
        self.config_dir = config_dir

    def load_config(self, filename: str = "workflow.yaml") -> dict[str, Any]:
        """
        Load YAML configuration dictionary.

        NOTE (correction): this used to return the same default dict
        (`{"mode": "operational", "auto_restart": True}`) whether the
        file genuinely didn't exist OR it existed but failed to parse
        (malformed YAML, a real read error, real content that wasn't a
        mapping) - with zero logging either way. A real config file
        with a real syntax error would silently be replaced by these
        made-up defaults, indistinguishable from a legitimate "no
        config provided" case - found via a repo-wide scan for
        `except Exception: pass`, not assumed. Now logs a warning with
        the real failure reason whenever a file that actually exists
        could not be used - only a genuinely missing file stays silent
        (that is the honest default case).
        """
        path = os.path.join(self.config_dir, filename)
        if os.path.exists(path):
            try:
                with open(path, encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                if isinstance(data, dict):
                    return data
                logger.warning(
                    "Config file %s did not contain a real YAML mapping (got %s) - using the honest default instead",
                    path, type(data).__name__,
                )
            except Exception:
                logger.warning("Failed to load config file %s - using the honest default instead", path, exc_info=True)
        return dict(_DEFAULT_CONFIG)
