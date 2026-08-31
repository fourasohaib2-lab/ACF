"""
Unit test suite for ESOCController.handle_run_climate()'s ssp-parameter fix.

REWRITTEN: `ssp` was accepted but never used - the registry's "ssp_engine"
module is a single SSPEngine instance constructed once at startup with a
hard-coded SSP2-4.5 scenario (module_registry.py), and
SSPEngine.evaluate_horizon(target_year) has no way to take a scenario per
call (the scenario is bound at SSPEngine.__init__ time). Any `ssp` value
passed to handle_run_climate() - e.g. "SSP5-8.5" - silently evaluated
SSP2-4.5 instead, regardless of the caller's actual request. Fixed by
constructing a scenario-specific SSPEngine for the requested `ssp` on each
call.
"""

import pytest

from acf.gui.esoc.command_dispatcher import CommandDispatcher
from acf.gui.esoc.esoc_controller import ESOCController
from acf.gui.esoc.esoc_workspace import WorkspaceManager
from acf.gui.esoc.module_registry import ModuleRegistry
from acf.gui.esoc.session_manager import SessionManager


@pytest.fixture
def controller():
    registry = ModuleRegistry()
    dispatcher = CommandDispatcher()
    workspace = WorkspaceManager()
    session = SessionManager()
    return ESOCController(registry, dispatcher, workspace, session)


def test_run_climate_default_scenario(controller):
    result = controller.handle_run_climate()
    assert result["status"] == "SUCCESS"
    assert result["projection"]["scenario"] == "SSP2-4.5"


def test_run_climate_honors_the_requested_scenario_not_always_default(controller):
    """CORRECTED: used to always evaluate SSP2-4.5 regardless of the `ssp` argument."""
    result = controller.handle_run_climate("SSP5-8.5")
    assert result["status"] == "SUCCESS"
    assert result["projection"]["scenario"] == "SSP5-8.5"


def test_run_climate_different_scenarios_give_genuinely_different_warming(controller):
    """
    Higher-emission scenarios must project more warming than lower-emission
    ones - the exact original bug (all scenarios silently evaluated
    identically) would make these all equal.
    """
    low = controller.handle_run_climate("SSP1-1.9")
    mid = controller.handle_run_climate("SSP2-4.5")
    high = controller.handle_run_climate("SSP5-8.5")

    t_low = low["projection"]["global_temp_anomaly_c"]
    t_mid = mid["projection"]["global_temp_anomaly_c"]
    t_high = high["projection"]["global_temp_anomaly_c"]

    assert t_low < t_mid < t_high


def test_run_climate_rejects_unknown_scenario_with_a_clear_error(controller):
    result = controller.handle_run_climate("NOT_A_REAL_SSP")
    assert result["status"] == "ERROR"
    assert "NOT_A_REAL_SSP" in result["reason"]
