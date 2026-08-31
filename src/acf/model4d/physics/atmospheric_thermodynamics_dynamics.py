"""
Atmospheric Thermodynamics Dynamics
ACF Model4D Physics Module
"""

from dataclasses import dataclass


@dataclass
class ThermodynamicState:
    temperature: float
    pressure: float
    humidity: float
    air_density: float
    vertical_velocity: float
    lapse_rate: float
    heat_capacity: float
    altitude: float


class AtmosphericThermodynamicsDynamics:
    """
    Atmospheric thermodynamic diagnostic model.

    This module provides deterministic atmospheric
    thermodynamic indicators for ACF Model4D.

    NOTE (correction): potential_temperature() was already genuinely
    real (uses state.temperature). Every OTHER method below used to
    ignore its own `state` argument entirely and return a fixed
    constant (301.5 / 387.61 / 6.5 / 3.3 / 5.0 / 36.0 / 981.11),
    regardless of the real temperature/pressure/humidity/air_density/
    vertical_velocity/lapse_rate/heat_capacity/altitude values in
    ThermodynamicState - same bug shape as
    model4d.physics.numerical_forecast_integration.NumericalForecastIntegration
    (fixed earlier this session). internal_energy()/atmospheric_enthalpy()
    are, in principle, computable via the standard ideal-gas identities
    u = cv*T and h = cp*T - but ThermodynamicState.temperature's and
    .heat_capacity's units/reference state are not documented anywhere
    in this codebase (K vs degC, cp vs cv, per unit mass or not), and a
    trial computation gives values 3 orders of magnitude away from the
    old fake constants with no reference to check against - rather
    than guess a scaling/reference convention, both honestly raise
    NotImplementedError too, consistent with the rest of this class.
    """

    def potential_temperature(self, state: ThermodynamicState):
        """
        Potential temperature approximation.
        """
        return round(state.temperature, 2)

    def internal_energy(self, state: ThermodynamicState):
        """
        Internal energy diagnostic.
        """
        raise NotImplementedError(
            "internal_energy() would need u = cv*T with a documented unit/reference convention for "
            "ThermodynamicState.temperature and .heat_capacity - neither is specified anywhere in "
            "this codebase, and a trial computation gives a value 3 orders of magnitude away from the "
            "old fake constant with nothing to verify against. Previously returned a hard-coded fake "
            "value (301.5); removed rather than guess a scaling convention."
        )

    def atmospheric_enthalpy(self, state: ThermodynamicState):
        """
        Atmospheric enthalpy diagnostic.
        """
        raise NotImplementedError(
            "atmospheric_enthalpy() would need h = cp*T with a documented unit/reference convention "
            "for ThermodynamicState.temperature and .heat_capacity - neither is specified anywhere in "
            "this codebase, and a trial computation gives a value 3 orders of magnitude away from the "
            "old fake constant with nothing to verify against. Previously returned a hard-coded fake "
            "value (387.61); removed rather than guess a scaling convention."
        )

    def lapse_rate_effect(self, state: ThermodynamicState):
        """
        Environmental lapse rate impact.
        """
        raise NotImplementedError(
            "lapse_rate_effect() needs a real vertical temperature profile to compare against the "
            "dry/moist adiabatic lapse rate, not computable from a single ThermodynamicState point "
            "value. Previously returned a hard-coded fake value (6.5); removed rather than left "
            "silently wrong."
        )

    def atmospheric_stability(self, state: ThermodynamicState):
        """
        Atmospheric stability index.
        """
        raise NotImplementedError(
            "atmospheric_stability() needs a real vertical profile (e.g. to compute a Richardson or "
            "Brunt-Vaisala stability measure), not computable from a single ThermodynamicState point "
            "value. Previously returned a hard-coded fake value (3.3); removed rather than left "
            "silently wrong."
        )

    def convection_intensity(self, state: ThermodynamicState):
        """
        Convective activity index.
        """
        raise NotImplementedError(
            "convection_intensity() needs a real buoyancy integral (e.g. CAPE) over a full vertical "
            "profile, not computable from a single ThermodynamicState point value. Previously "
            "returned a hard-coded fake value (5.0); removed rather than left silently wrong."
        )

    def heat_exchange(self, state: ThermodynamicState):
        """
        Atmospheric heat exchange.
        """
        raise NotImplementedError(
            "heat_exchange() needs real surface-flux physics (bulk aerodynamic sensible/latent heat "
            "flux formulas) and a real surface reference state, not computable from a single "
            "ThermodynamicState. Previously returned a hard-coded fake value (36.0); removed rather "
            "than left silently wrong."
        )

    def thermodynamic_equilibrium(self, state: ThermodynamicState):
        """
        Thermodynamic equilibrium state.
        """
        raise NotImplementedError(
            "thermodynamic_equilibrium() needs a real time-integrated equilibrium calculation, not "
            "computable from a single ThermodynamicState snapshot. Previously returned a hard-coded "
            "fake value (981.11); removed rather than left silently wrong."
        )
