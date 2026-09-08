"""
REWRITTEN: every method used to ignore its own `state` argument and
return a fixed constant (301.5/8.5/1012.5/12.0/6.5/45.0/25.0/9.5)
regardless of the real state passed in - same bug shape as the
already-fixed
model4d.physics.numerical_forecast_integration.NumericalForecastIntegration.
A real dynamical-core tendency needs the spatial grid (advection,
pressure-gradient terms) and physical parameterization tendencies, not
just a single point state - so each method now honestly raises
NotImplementedError instead of returning an invented number.
"""

import pytest

from acf.model4d.physics.atmospheric_dynamics_core import (
    AtmosphericDynamicsCore,
    AtmosphericDynamicsState,
)


def create_state():

    return AtmosphericDynamicsState(
        temperature=300,
        humidity=12,
        pressure=100000,
        wind_speed=10,
        vertical_velocity=3,
        radiation_flux=250,
        convection=5,
        precipitation=4,
        surface_energy=320,
    )


def test_temperature_dynamics_not_implemented():

    model = AtmosphericDynamicsCore()

    with pytest.raises(NotImplementedError):
        model.temperature_dynamics(create_state())


def test_humidity_transport_not_implemented():

    model = AtmosphericDynamicsCore()

    with pytest.raises(NotImplementedError):
        model.humidity_transport(create_state())


def test_pressure_dynamics_not_implemented():

    model = AtmosphericDynamicsCore()

    with pytest.raises(NotImplementedError):
        model.pressure_dynamics(create_state())


def test_wind_circulation_not_implemented():

    model = AtmosphericDynamicsCore()

    with pytest.raises(NotImplementedError):
        model.wind_circulation(create_state())


def test_vertical_convection_not_implemented():

    model = AtmosphericDynamicsCore()

    with pytest.raises(NotImplementedError):
        model.vertical_convection(create_state())


def test_energy_transport_not_implemented():

    model = AtmosphericDynamicsCore()

    with pytest.raises(NotImplementedError):
        model.energy_transport(create_state())


def test_mass_transport_not_implemented():

    model = AtmosphericDynamicsCore()

    with pytest.raises(NotImplementedError):
        model.mass_transport(create_state())


def test_dynamic_stability_index_not_implemented():

    model = AtmosphericDynamicsCore()

    with pytest.raises(NotImplementedError):
        model.dynamic_stability_index(create_state())
