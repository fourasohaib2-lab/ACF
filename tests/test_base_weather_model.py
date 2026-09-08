"""
Unit test suite for models.base_model.BaseWeatherModel's default Extended
Universal NWP Lifecycle API (ACF-NWP-001).

REWRITTEN: prepare()/run()/restart()/stop()/resume() used to
unconditionally claim a successful lifecycle transition
("PREPARED"/"RUNNING"/"RESTARTED"/True) regardless of any real
dynamic-core solver, scheduler, or checkpoint backend connected.
verify() used to unconditionally return a PERFECT score (rmse=0.0,
bias=0.0, mae=0.0, acc=1.0) with no real observations ever compared -
the same fake-stub pattern found and fixed throughout this session.
None of the four concrete subclasses (ARPEGEIngestionAdapter,
AROMEIngestionAdapter, ALADINIngestionAdapter, ERA5Model) override
these methods (verified), so all of them previously inherited this
fabricated behavior. See base_model.py's NOTE (correction) docstrings
for what each used to fabricate.
"""

import pytest

from acf.models.base_model import BaseWeatherModel


class _MinimalConcreteModel(BaseWeatherModel):
    """Smallest possible concrete subclass implementing only the abstract interface."""

    name = "TestModel"

    def detect(self, dataset):
        return True

    def variables(self):
        return ["t2m"]

    def levels(self):
        return [1000]

    def projection(self):
        return "lambert"


def test_prepare_no_longer_claims_success():
    result = _MinimalConcreteModel().prepare({"domain": "FRANCE"})
    assert result["status"] == "NOT_PREPARED_NO_BACKEND_CONNECTED"
    assert result["model"] == "TestModel"


def test_configure_still_genuinely_echoes_its_inputs():
    """configure() genuinely uses all three parameters - no fabrication, left unchanged."""
    result = _MinimalConcreteModel().configure(domain="FRANCE", resolution=1.3, forecast_hours=24)
    assert result == {"domain": "FRANCE", "resolution": 1.3, "forecast_hours": 24}


def test_run_no_longer_claims_running():
    result = _MinimalConcreteModel().run()
    assert result["status"] == "NOT_RUNNING_NO_SOLVER_CONNECTED"


def test_restart_no_longer_claims_success():
    result = _MinimalConcreteModel().restart(checkpoint_step=12)
    assert result["status"] == "NOT_RESTARTED_NO_BACKEND_CONNECTED"
    assert result["checkpoint_step"] == 12


def test_stop_and_resume_no_longer_unconditionally_true():
    model = _MinimalConcreteModel()
    assert model.stop() is False
    assert model.resume() is False


def test_collect_outputs_returns_empty_not_fabricated():
    assert _MinimalConcreteModel().collect_outputs("/tmp/some_dir") == []


def test_verify_no_longer_returns_a_fake_perfect_score():
    """
    CORRECTED (safety-relevant): used to unconditionally claim a
    PERFECT verification score (rmse=0.0, bias=0.0, mae=0.0, acc=1.0)
    with no real observation dataset ever compared.
    """
    with pytest.raises(NotImplementedError):
        _MinimalConcreteModel().verify()
