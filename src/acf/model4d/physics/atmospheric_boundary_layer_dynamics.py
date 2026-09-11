"""
Atmospheric Boundary Layer Dynamics
Sprint 9.13

Module:
- turbulence
- sensible heat flux
- latent heat flux
- vertical mixing
- surface-atmosphere exchange
"""

from dataclasses import dataclass


@dataclass
class BoundaryLayerState:
    """
    Atmospheric boundary layer state variables.
    """

    wind_speed: float
    temperature_difference: float
    humidity_difference: float
    surface_roughness: float
    stability: float = 1.0


class AtmosphericBoundaryLayerDynamics:
    """
    Simplified atmospheric boundary layer physics model.

    NOTE (found, NOT changed — Physics Guard, found during the
    post-model4d audit, 2026-09-11): every formula below uses an
    uncited proportionality coefficient (0.1, 0.2666666667, 0.4, and a
    flat "surface_correction = 1.0" subtracted in surface_exchange())
    that does not correspond to any real physical constant except the
    0.4 in vertical_mixing() (plausibly von Kármán's constant, κ≈0.4,
    though the formula it's used in is not a standard named one this
    audit could verify). This is a materially different, simpler model
    than this same package's own real bulk-transfer formulas
    (acf.model4d.physics.surface_flux.SurfaceFlux, same directory):
    SurfaceFlux.sensible_heat_flux() computes H = rho*Cp*Ch*(Ts-Ta)
    with real, cited air density/specific heat constants
    (rho=1.225 kg/m3, Cp=1004 J/(kg K)); this class's own
    sensible_heat_flux() computes wind_speed*temperature_difference*0.1
    instead - a different formula for the same-named physical quantity,
    with no shared constant and no citation for 0.1. Zero real callers
    anywhere in the codebase beyond this class's own dedicated test
    (tests/test_atmospheric_boundary_layer_dynamics.py, which only
    locks in these formulas' own output - not a physics reference
    value) - verified via grep. Left in place rather than replacing
    these coefficients with a guessed "properly sourced" set, or
    silently aligning this class with SurfaceFlux's real formulas
    without a real spec calling for that merge.
    """

    def __init__(self):

        self.name = "Atmospheric Boundary Layer Dynamics"

    def turbulence_intensity(self, state: BoundaryLayerState) -> float:
        """
        Turbulence intensity estimation.
        """

        value = state.wind_speed * state.surface_roughness * 0.1

        return round(value, 3)

    def sensible_heat_flux(self, state: BoundaryLayerState) -> float:
        """
        Sensible heat exchange between surface and atmosphere.
        """

        value = state.wind_speed * state.temperature_difference * 0.1

        return round(value, 3)

    def latent_heat_flux(self, state: BoundaryLayerState) -> float:
        """
        Latent heat flux due to humidity transport.
        """

        value = state.wind_speed * state.humidity_difference * state.surface_roughness * 0.2666666667

        return round(value, 3)

    def vertical_mixing(self, state: BoundaryLayerState) -> float:
        """
        Vertical turbulent mixing coefficient.
        """

        value = state.wind_speed * state.surface_roughness * 0.4 / state.stability

        return round(value, 3)

    def surface_exchange(self, state: BoundaryLayerState) -> float:
        """
        Total surface-atmosphere exchange.

        Includes:
        - sensible heat
        - latent heat
        - surface correction
        """

        sensible = self.sensible_heat_flux(state)

        latent = self.latent_heat_flux(state)

        surface_correction = 1.0

        value = sensible + latent - surface_correction

        return round(value, 3)
