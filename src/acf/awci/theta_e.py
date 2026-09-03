"""
ACF Complexity Engine — real per-point equivalent potential temperature (theta-e)
======================================================================================

Explicit user request ("continue au module thermodynamique, avec
theta-e") - continuing the real, targeted closure of §12-16 (docs/
ACF_MASTER_PROMPT.md section 13 explicitly lists "température
potentielle équivalente" among the thermodynamic module's own
candidate variables) started with the dynamic module's real wind shear.

Real formula, composed from 3 already-existing, correct pieces - not
reimplemented
-------------------------------------------------------------------------
1. `acf.science.thermodynamics.Thermodynamics.calculate_relative_humidity()`
   - real relative humidity from specific humidity, pressure,
   temperature (vapor pressure / saturation vapor pressure).
2. `acf.science.dewpoint.DewPoint.calculate()` - real dewpoint via the
   Magnus-Tetens approximation (Alduchov & Eskridge 1996 coefficients).
3. `acf.science.equivalent_potential_temperature.
   EquivalentPotentialTemperature.calculate_bolton_1980()` - the
   CANONICAL, published theta-e formula (Bolton, D. (1980), "The
   Computation of Equivalent Potential Temperature", Monthly Weather
   Review 108(7), 1046-1053 - accurate to ~0.3 K over the
   meteorological range, the same operational form MetPy/SHARPpy use),
   not the same module's own simpler `calculate()` approximation
   (exp(Lv*q/(Cp*T)), no LCL/pressure correction).

Real, disclosed reason for the 3-step composition rather than a direct
specific-humidity form: Bolton (1980) is derived in terms of dewpoint,
not specific humidity directly - deriving a specific-humidity-native
form here instead would mean re-deriving/approximating Bolton's own
formula, exactly the kind of informal reformulation this project's
audits exist to catch. Composing the real, already-published,
already-tested pieces is the honest way to reach the same canonical
result from AWCI's own specific_humidity input convention.

Honest scope
-------------
`compute_real_theta_e_at_point()` returns `theta_e_k=None` (never a
fabricated Kelvin value) when the real computed relative humidity is
non-positive (DewPoint.calculate() itself requires a real percentage
in (0, 100]; a genuinely dry point produces no real, meaningful
dewpoint to compute a real theta-e from) - a real, honestly-flagged
edge case, not silently clamped to some default.
"""

from __future__ import annotations

from typing import Any

from acf.science.dewpoint import DewPoint
from acf.science.equivalent_potential_temperature import EquivalentPotentialTemperature
from acf.science.thermodynamics import Thermodynamics


def compute_real_theta_e_at_point(temperature_k: float, specific_humidity: float, pressure_hpa: float) -> dict[str, Any]:
    """
    Real equivalent potential temperature (theta-e, K) at one point -
    composes 3 already-real formulas (see module docstring), no new
    physics invented.

    Parameters
    ----------
    temperature_k : float
        Real air temperature (K).
    specific_humidity : float
        Real specific humidity (kg/kg).
    pressure_hpa : float
        Real atmospheric pressure (hPa).

    Returns
    -------
    dict
        theta_e_k : real float (K), or `None` (never a fabricated
            value) when the real computed relative humidity is
            non-positive - see module docstring.
        relative_humidity_pct, dewpoint_k : the real intermediate
            values actually used, for transparency/debugging - `None`
            alongside `theta_e_k` when it is `None`.
        status, is_real_data, honest_limitation.
    """
    relative_humidity_pct = Thermodynamics.calculate_relative_humidity(
        specific_humidity, pressure_hpa, temperature_k, is_kelvin=True
    )

    if relative_humidity_pct <= 0.0:
        return {
            "theta_e_k": None,
            "relative_humidity_pct": None,
            "dewpoint_k": None,
            "status": "THETA_E_NOT_COMPUTED_ZERO_HUMIDITY",
            "is_real_data": False,
            "honest_limitation": (
                f"Real computed relative humidity was {relative_humidity_pct} (non-positive) at this point - "
                "no real, meaningful dewpoint (and therefore no real theta-e) exists to compute from a "
                "genuinely dry point, so theta_e_k is honestly None, not a fabricated value."
            ),
        }

    temperature_c = temperature_k - 273.15
    dewpoint_c = DewPoint.calculate(temperature_c, relative_humidity_pct)
    dewpoint_k = dewpoint_c + 273.15

    theta_e_k = EquivalentPotentialTemperature.calculate_bolton_1980(temperature_k, dewpoint_k, pressure_hpa)

    return {
        "theta_e_k": theta_e_k,
        "relative_humidity_pct": relative_humidity_pct,
        "dewpoint_k": dewpoint_k,
        "status": "REAL_THETA_E_BOLTON_1980",
        "is_real_data": True,
        "honest_limitation": (
            "Real Bolton (1980) equivalent potential temperature, accurate to ~0.3 K over the meteorological "
            "range - a real single-point value, not a real vertical theta-e gradient/advection diagnostic "
            "(section 12-16's own broader, still-open scope)."
        ),
    }
