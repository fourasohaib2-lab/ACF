"""
REWRITTEN: potential_temperature() was already genuinely real (uses
state.temperature) - its test is unchanged. Every OTHER method used to
ignore its own `state` argument and return a fixed constant
(301.5/387.61/6.5/3.3/5.0/36.0/981.11) regardless of the real state
passed in - same bug shape as the already-fixed
model4d.physics.numerical_forecast_integration.NumericalForecastIntegration.
internal_energy()/atmospheric_enthalpy() are, in principle, computable
via u=cv*T / h=cp*T, but ThermodynamicState's unit/reference
convention is undocumented and a trial computation lands 3 orders of
magnitude away from the old fake constants with nothing to verify
against - rather than guess, both honestly raise NotImplementedError
too, like the rest of this class.
"""

import pytest

from acf.model4d.physics.atmospheric_thermodynamics_dynamics import (
    AtmosphericThermodynamicsDynamics,
    ThermodynamicState,
)


def create_state():

    return ThermodynamicState(
        temperature=300,
        pressure=1000,
        humidity=50,
        air_density=1.2,
        vertical_velocity=10,
        lapse_rate=6.5,
        heat_capacity=1005,
        altitude=1000,
    )


def test_potential_temperature():
    """Genuinely real - uses state.temperature. Unaffected by this fix."""

    model = AtmosphericThermodynamicsDynamics()

    assert model.potential_temperature(create_state()) == 300.0


def test_internal_energy_not_implemented():

    model = AtmosphericThermodynamicsDynamics()

    with pytest.raises(NotImplementedError):
        model.internal_energy(create_state())


def test_atmospheric_enthalpy_not_implemented():

    model = AtmosphericThermodynamicsDynamics()

    with pytest.raises(NotImplementedError):
        model.atmospheric_enthalpy(create_state())


def test_lapse_rate_effect_not_implemented():

    model = AtmosphericThermodynamicsDynamics()

    with pytest.raises(NotImplementedError):
        model.lapse_rate_effect(create_state())


def test_atmospheric_stability_not_implemented():

    model = AtmosphericThermodynamicsDynamics()

    with pytest.raises(NotImplementedError):
        model.atmospheric_stability(create_state())


def test_convection_intensity_not_implemented():

    model = AtmosphericThermodynamicsDynamics()

    with pytest.raises(NotImplementedError):
        model.convection_intensity(create_state())


def test_heat_exchange_not_implemented():

    model = AtmosphericThermodynamicsDynamics()

    with pytest.raises(NotImplementedError):
        model.heat_exchange(create_state())


def test_thermodynamic_equilibrium_not_implemented():

    model = AtmosphericThermodynamicsDynamics()

    with pytest.raises(NotImplementedError):
        model.thermodynamic_equilibrium(create_state())
