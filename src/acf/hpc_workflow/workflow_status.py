"""HPC Workflow Status & Errors (ACF-HPC-104)."""

from enum import Enum


class WorkflowStatus(Enum):
    """Execution status enum for HPC workflows."""

    INITIALIZING = "INITIALIZING"
    SUBMITTED = "SUBMITTED"
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETING = "COMPLETING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    TIMEOUT = "TIMEOUT"
    NODE_FAILURE = "NODE_FAILURE"


class WorkflowError(Exception):
    """Base exception for HPC Workflow errors."""


class WorkflowValidationError(WorkflowError):
    """Validation exception for input/environment checks."""


class WorkflowExecutionError(WorkflowError):
    """Runtime execution exception during job run."""
