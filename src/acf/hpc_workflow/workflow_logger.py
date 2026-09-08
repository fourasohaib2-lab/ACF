"""Structured JSON & Text Workflow Logger (ACF-HPC-104)."""

import json
import logging
import time
from typing import Any

logger = logging.getLogger("acf.hpc_workflow")


class WorkflowLogger:
    """Logs structured JSON and operational text events for workflows."""

    def log_event(self, event_type: str, details: dict[str, Any]) -> None:
        """Log structured JSON event."""
        payload = {"timestamp": time.time(), "event_type": event_type, "details": details}
        logger.info(json.dumps(payload))
