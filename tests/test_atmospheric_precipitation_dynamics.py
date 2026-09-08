"""
Atmospheric Precipitation Dynamics
Sprint 9.21

REWRITTEN: this file used to contain only a stray, out-of-date
duplicate copy of PrecipitationState/AtmosphericPrecipitationDynamics
with zero `def test_*` functions - pytest collected the file but ran
no tests from it, so the real source module had 0% coverage and was
never actually verified. The duplicate had also drifted out of sync
with the real source (different field/method names entirely),
confirming it was stale copy-paste content rather than a real
reference. Replaced with real tests importing and exercising the
actual current source class.
"""

import pytest

from acf.model4d.physics.atmospheric_precipitation_dynamics import (
    AtmosphericPrecipitationDynamics,
    PrecipitationState,
)


@pytest.fixture
def dynamics():
    return AtmosphericPrecipitationDynamics()


@pytest.fixture
def state():
    return PrecipitationState(
        humidity=0.8, condensation_rate=2.0, convection_intensity=1.5, precipitation_efficiency=0.6
    )


def test_condensation_amount(dynamics, state):
    result = dynamics.condensation_amount(state)
    assert result == pytest.approx(state.humidity * state.condensation_rate * 0.1)


def test_precipitation_rate(dynamics, state):
    result = dynamics.precipitation_rate(state)
    expected = round(
        state.humidity * state.condensation_rate * state.convection_intensity * state.precipitation_efficiency * 0.1,
        2,
    )
    assert result == pytest.approx(expected)


def test_precipitation_efficiency_method(dynamics, state):
    result = dynamics.precipitation_efficiency(state)
    assert result == pytest.approx(state.condensation_rate * state.convection_intensity * state.precipitation_efficiency)


def test_water_state(dynamics, state):
    result = dynamics.water_state(state)
    assert result == pytest.approx(state.humidity * state.condensation_rate)


def test_cloud_conversion(dynamics, state):
    result = dynamics.cloud_conversion(state)
    assert result == pytest.approx(round(state.humidity * state.precipitation_efficiency * 0.05, 2))


def test_precipitation_state_default_efficiency():
    default_state = PrecipitationState(humidity=0.5, condensation_rate=1.0, convection_intensity=1.0)
    assert default_state.precipitation_efficiency == 1.0
