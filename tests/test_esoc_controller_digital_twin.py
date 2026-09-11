"""
Unit test suite for ESOCController.handle_load_digital_twin() - backs the
ESOC toolbar's "🌐 Digital Twin" action and DigitalTwinPanel's own
"🔮 Load Digital Twin Scenario" button (panel_manager.py).

CORRECTED (2026-09-11, found during a full ESOC rescan): used to
unconditionally return {"status": "SUCCESS", "scenario": scenario} without
ever touching the real, registered "digital_twin" module
(DigitalTwinEngine) - a fabricated success for a scenario that was never
actually loaded. Now genuinely calls the real
DigitalTwinEngine.run_digital_twin_cycle() and passes its own honest
status through, same "real engine call, honestly disclosed limitation"
pattern as handle_run_simulation()/handle_refresh_observations().
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.digital_twin.digital_twin_engine import DigitalTwinEngine
from acf.gui.esoc.command_dispatcher import CommandDispatcher
from acf.gui.esoc.esoc_controller import ESOCController
from acf.gui.esoc.esoc_workspace import WorkspaceManager
from acf.gui.esoc.module_registry import ModuleRegistry
from acf.gui.esoc.session_manager import SessionManager


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def controller(qapp):
    registry = ModuleRegistry()
    dispatcher = CommandDispatcher()
    workspace = WorkspaceManager()
    session = SessionManager()
    return ESOCController(registry, dispatcher, workspace, session)


def test_load_digital_twin_genuinely_calls_the_real_engine_not_a_fabricated_success(controller):
    """The real regression guard: this must NOT be the literal string
    "SUCCESS" for a scenario that was never actually run - it must be
    DigitalTwinEngine.run_digital_twin_cycle()'s own honest status."""
    result = controller.handle_load_digital_twin("2050 Mid-Century Horizon")

    assert result["status"] == "NOT_RUN_NO_ASSIMILATION_FORECAST_CYCLE_CONNECTED"
    assert result["is_real_data"] is False
    assert result["scenario"] == "2050 Mid-Century Horizon"


def test_load_digital_twin_result_matches_a_direct_independent_engine_call(controller):
    """Cross-check discipline: the controller's own result must equal a
    fresh, independent direct call to the real underlying engine -
    never a separately re-derived/hand-typed value."""
    expected = DigitalTwinEngine().run_digital_twin_cycle()

    result = controller.handle_load_digital_twin("Present Earth Digital Twin (t=0)")

    assert result["engine"] == expected["engine"]
    assert result["status"] == expected["status"]
    assert result["is_real_data"] == expected["is_real_data"]
    assert result["simulation"]["horizon"] == expected["simulation"]["horizon"]


def test_load_digital_twin_reports_an_honest_error_if_the_engine_is_missing(controller):
    controller.registry.modules.pop("digital_twin", None)

    result = controller.handle_load_digital_twin("Historical Replay (1950 - Present)")

    assert result["status"] == "ERROR"
    assert "not found" in result["message"].lower()
