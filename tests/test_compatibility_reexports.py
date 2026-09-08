"""
Atmospheric Complexity Framework (ACF)

Compatibility Re-export Module Test Suite

These small modules previously had 0% coverage: each is a thin
compatibility shim re-exporting a class defined elsewhere under a
legacy/alternate import path. Verifies each shim actually points at
the real class (unlike the dead X.py-shadowed-by-X/-package modules
found and flagged earlier this session, none of these collide with a
same-named package, so they are genuinely reachable).
"""

from acf.hpc_connector.environment_manager import ModuleLoader as RealModuleLoader
from acf.hpc_connector.module_loader import ModuleLoader
from acf.hpc_workflow.workflow_archive import WorkflowCleanup as RealWorkflowCleanup
from acf.hpc_workflow.workflow_cleanup import WorkflowCleanup
from acf.hpc_workflow.workflow_context import WorkflowProgress as RealWorkflowProgress
from acf.hpc_workflow.workflow_events import WorkflowNotifications
from acf.hpc_workflow.workflow_history import WorkflowHistory
from acf.hpc_workflow.workflow_notifications import WorkflowNotifications as RealWorkflowNotifications
from acf.hpc_workflow.workflow_progress import WorkflowProgress
from acf.hpc_workflow.workflow_registry import WorkflowHistory as RealWorkflowHistory
from acf.importers.manager import DataManager as RealDataManager
from acf.io.manager import DataManager
from acf.model4d.exceptions import (
    CoordinateOutOfBoundsError,
    GridDimensionMismatchError,
    InterpolationError,
    Model4DError,
    OperatorError,
)
from acf.core.exceptions import ACFError


def test_reexports_point_at_the_real_classes():
    assert ModuleLoader is RealModuleLoader
    assert WorkflowCleanup is RealWorkflowCleanup
    assert WorkflowNotifications is RealWorkflowNotifications
    assert WorkflowHistory is RealWorkflowHistory
    assert WorkflowProgress is RealWorkflowProgress
    assert DataManager is RealDataManager


def test_model4d_exception_hierarchy():
    for exc_cls in (
        GridDimensionMismatchError,
        CoordinateOutOfBoundsError,
        InterpolationError,
        OperatorError,
    ):
        assert issubclass(exc_cls, Model4DError)
        assert issubclass(exc_cls, ACFError)
