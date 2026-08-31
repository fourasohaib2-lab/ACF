"""
REWRITTEN: every method used to ignore its own `state` argument and
return a fixed constant (18.5/245/310.0/7.5/35.0/12.8) regardless of
the real state passed in - same bug shape as the already-fixed
model4d.physics.numerical_forecast_integration.NumericalForecastIntegration.
A real Earth-system coupling coefficient needs the spatial grid and
real physical exchange formulas, not just a single point state - so
each method now honestly raises NotImplementedError instead of
returning an invented number.
"""

import pytest

from acf.model4d.physics.advanced_climate_coupling import (
    AdvancedClimateCoupling,
    AdvancedClimateState,
)


def create_state():

    return AdvancedClimateState(
        temperature=300,
        humidity=15,
        cloud_cover=30,
        radiation_flux=260,
        convection=3,
        precipitation=8,
        ocean_feedback=20,
        surface_energy=350,
    )


def test_atmosphere_ocean_coupling_not_implemented():

    model = AdvancedClimateCoupling()

    with pytest.raises(NotImplementedError):
        model.atmosphere_ocean_coupling(create_state())


def test_cloud_feedback_coupling_not_implemented():

    model = AdvancedClimateCoupling()

    with pytest.raises(NotImplementedError):
        model.cloud_feedback_coupling(create_state())


def test_radiation_energy_balance_not_implemented():

    model = AdvancedClimateCoupling()

    with pytest.raises(NotImplementedError):
        model.radiation_energy_balance(create_state())


def test_moisture_climate_coupling_not_implemented():

    model = AdvancedClimateCoupling()

    with pytest.raises(NotImplementedError):
        model.moisture_climate_coupling(create_state())


def test_ocean_heat_transport_not_implemented():

    model = AdvancedClimateCoupling()

    with pytest.raises(NotImplementedError):
        model.ocean_heat_transport(create_state())


def test_climate_stability_index_not_implemented():

    model = AdvancedClimateCoupling()

    with pytest.raises(NotImplementedError):
        model.climate_stability_index(create_state())
