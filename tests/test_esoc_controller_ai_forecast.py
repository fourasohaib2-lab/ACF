"""
Unit test suite for ESOCController.handle_run_ai_forecast()'s dummy-state fix.

REWRITTEN: this used to feed a fabricated, disconnected `{"T": 288.0}`
scalar into NeuralOperatorEngine.predict_next_state() regardless of any
real atmospheric state - and since it wasn't even a numpy array,
predict_next_state()'s own logic passes non-array fields through completely
unchanged, so this call never even exercised the neural operator's real
FFT-based prediction path (a complete no-op returning the same 288.0 back).
It still unconditionally claimed "SUCCESS". Fixed to use
AtmosphericModel.initialize_state() (a genuine, physically-consistent,
properly-shaped array state) as the input instead.
"""

import numpy as np

from acf.gui.esoc.command_dispatcher import CommandDispatcher
from acf.gui.esoc.esoc_controller import ESOCController
from acf.gui.esoc.esoc_workspace import WorkspaceManager
from acf.gui.esoc.module_registry import ModuleRegistry
from acf.gui.esoc.session_manager import SessionManager


def _make_controller():
    registry = ModuleRegistry()
    dispatcher = CommandDispatcher()
    workspace = WorkspaceManager()
    session = SessionManager()
    return ESOCController(registry, dispatcher, workspace, session)


def test_ai_forecast_no_longer_uses_a_disconnected_dummy_scalar():
    controller = _make_controller()
    result = controller.handle_run_ai_forecast()

    assert result["status"] == "SUCCESS"
    assert result["input_state_source"] == "AtmosphericModel.initialize_state() baseline"


def test_ai_forecast_output_contains_genuine_array_fields_not_a_passthrough_scalar():
    """
    CORRECTED: the old dummy_state = {"T": 288.0} was a bare float, so
    predict_next_state() passed it through unchanged (a no-op). The real
    AtmosphericModel state has array-valued fields (T, P, U, V, q, ...),
    so the neural operator's FFT-based prediction path now genuinely runs.
    """
    controller = _make_controller()
    result = controller.handle_run_ai_forecast()

    output = result["output"]
    assert "T" in output
    assert isinstance(output["T"], np.ndarray)
    assert output["T"].shape[0] > 1  # a real multi-level/multi-point field, not a scalar


def test_ai_forecast_temperature_field_is_physically_plausible():
    """The input state comes from a real standard-atmosphere baseline - output should stay in a sane range."""
    controller = _make_controller()
    result = controller.handle_run_ai_forecast()

    temp_field = result["output"]["T"]
    assert np.all(temp_field > 150.0)  # well above absolute zero / unphysically cold
    assert np.all(temp_field < 350.0)  # well below unphysically hot


def test_ai_forecast_uses_the_real_trained_fno_surrogate():
    """Added this session alongside the real, trained FNO surrogate
    (acf.ai.simulation.fno_model/fno_training): ModuleRegistry loads the
    reference checkpoint if present, and handle_run_ai_forecast() now
    also reports a genuine prediction from it (on state["T"][0], the
    surface level - see fno_training.py's own docstring), separate from
    predict_next_state()'s general untrained proxy in "output"."""
    controller = _make_controller()
    result = controller.handle_run_ai_forecast()

    surrogate = result["surface_temperature_surrogate"]
    assert surrogate["status"] == "PREDICTED_BY_TRAINED_SURROGATE"
    assert surrogate["surrogate_final_train_loss"] is not None
    assert "predicted_field" not in surrogate  # kept out of the dispatched dict (large array)
