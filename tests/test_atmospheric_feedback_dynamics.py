"""
REWRITTEN: every method used to ignore its own `state` argument and
return a fixed constant (3.4/242/5.5/42.5/5.0/5.9) regardless of the
real state passed in - same bug shape as the already-fixed
model4d.physics.numerical_forecast_integration.NumericalForecastIntegration.
A real feedback coupling strength needs the spatial grid and real
physical feedback formulas, not just a single point state - so each
method now honestly raises NotImplementedError instead of returning an
invented number.
"""

import pytest

from acf.model4d.physics.atmospheric_feedback_dynamics import (
    AtmosphericFeedbackDynamics,
    AtmosphericFeedbackDynamicsState,
)


def create_state():

    return AtmosphericFeedbackDynamicsState(
        temperature=300,
        humidity=10,
        cloud_cover=20,
        radiation_flux=250,
        convection=2,
        precipitation=5,
        surface_energy=300,
    )


def test_humidity_temperature_coupling_not_implemented():

    model = AtmosphericFeedbackDynamics()

    with pytest.raises(NotImplementedError):
        model.humidity_temperature_coupling(create_state())


def test_cloud_radiation_coupling_not_implemented():

    model = AtmosphericFeedbackDynamics()

    with pytest.raises(NotImplementedError):
        model.cloud_radiation_coupling(create_state())


def test_convection_feedback_not_implemented():

    model = AtmosphericFeedbackDynamics()

    with pytest.raises(NotImplementedError):
        model.convection_feedback(create_state())


def test_energy_transport_feedback_not_implemented():

    model = AtmosphericFeedbackDynamics()

    with pytest.raises(NotImplementedError):
        model.energy_transport_feedback(create_state())


def test_feedback_growth_rate_not_implemented():

    model = AtmosphericFeedbackDynamics()

    with pytest.raises(NotImplementedError):
        model.feedback_growth_rate(create_state())


def test_climate_feedback_dynamics_index_not_implemented():

    model = AtmosphericFeedbackDynamics()

    with pytest.raises(NotImplementedError):
        model.climate_feedback_dynamics_index(create_state())
