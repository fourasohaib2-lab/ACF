"""
ACF - Atmospheric Complexity Framework

Sprint 9.26
Atmospheric Thermodynamics Engine

Model4D Physics Core
"""

import math
from dataclasses import dataclass

# ============================================================
# Constants
# ============================================================

RD = 287.05
RV = 461.5
CP = 1004.0
G = 9.80665
LV = 2.5e6
P0 = 100000.0


# ============================================================
# State
# ============================================================


@dataclass
class ThermodynamicsState:
    temperature: float
    pressure: float
    specific_humidity: float
    height: float = 0.0


# ============================================================
# Engine
# ============================================================


class AtmosphericThermodynamics:
    def potential_temperature(self, state):

        theta = state.temperature * (P0 / state.pressure) ** (RD / CP)

        return round(theta, 2)

    def virtual_temperature(self, state):

        tv = state.temperature * (1 + 0.61 * state.specific_humidity)

        return round(tv, 2)

    def air_density(self, state):

        rho = state.pressure / (RD * self.virtual_temperature(state))

        return round(rho, 3)

    def dry_static_energy(self, state):

        s = CP * state.temperature + G * state.height

        return round(s, 2)

    def moist_static_energy(self, state):

        mse = CP * state.temperature + G * state.height + LV * state.specific_humidity

        return round(mse, 2)

    def enthalpy(self, state):

        h = CP * state.temperature + LV * state.specific_humidity

        return round(h, 2)

    def internal_energy(self, state):

        cv = CP - RD

        u = cv * state.temperature

        return round(u, 2)

    def adiabatic_lapse_rate(self):

        gamma = G / CP

        return round(gamma, 5)

    def moist_adiabatic_lapse_rate(self, state):
        """
        Saturated (moist) adiabatic lapse rate.

        NOTE (correction - Physics Guard): the standard formula
        (Rogers & Yau, "A Short Course in Cloud Physics"; AMS Glossary
        of Meteorology) is
        Gamma_s = (g/Cp) * [1 + Lv*w/(Rd*T)] / [1 + Lv^2*w/(Cp*Rv*T^2)]
        - the denominator here was already correct, but the numerator's
        bracketed latent-heat-release correction term
        "1 + Lv*w/(Rd*T)" was missing entirely (this used to just be
        "G / CP", i.e. an implicit numerator of 1). At T=280K, q=0.01
        kg/kg this understated the moist lapse rate by about 24%
        (~3.6 K/km instead of the correct ~4.7 K/km) - not a fudge
        factor, an incomplete formula. No test asserted a specific
        value (only `> 0`), so nothing was locked in.
        """

        numerator = (G / CP) * (1 + (LV * state.specific_humidity) / (RD * state.temperature))

        denominator = 1 + (LV**2 * state.specific_humidity / (CP * RV * state.temperature**2))

        gamma = numerator / denominator

        return round(gamma, 5)

    def lifting_condensation_level(self, temperature_celsius, dewpoint_celsius):

        lcl = 125 * (temperature_celsius - dewpoint_celsius)

        return round(lcl, 2)

    def brunt_vaisala_frequency(self, theta_gradient):

        if theta_gradient <= 0:
            return 0.0

        value = math.sqrt(G * theta_gradient)

        return round(value, 4)

    def convective_available_potential_energy(self, parcel_temperature, environment_temperature, height):

        if parcel_temperature <= environment_temperature:
            return 0.0

        cape = G * (parcel_temperature - environment_temperature) / environment_temperature * height

        return round(cape, 2)

    def convective_inhibition(self, temperature_deficit, height):

        cin = -G * temperature_deficit * height

        return round(cin, 2)

    def stability_index(self, theta_surface, theta_upper, height_difference):

        if height_difference == 0:
            return 0.0

        index = (theta_upper - theta_surface) / height_difference

        return round(index, 5)


# ============================================================
# API compatibility
# ============================================================

Thermodynamics = AtmosphericThermodynamics
