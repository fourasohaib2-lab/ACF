"""
Parcel Ascent & CAPE/CIN
========================

Genuine dry/moist-adiabatic parcel-ascent thermodynamics: CAPE, CIN,
LFC, EL, and the classic severe-weather sounding indices built on top
of a lifted parcel (K-Index, Total Totals, Showalter, Lifted Index).

This fills the gap explicitly flagged (not silently faked) in
radiosonde.py's SoundingProfile.surface_based_parcel_indices():
computing CAPE/CIN correctly requires simulating a parcel's ascent
along the moist adiabat above its LCL, not just integrating buoyancy
against the environmental trace itself. That parcel-ascent solver is
exactly what MetPy's ``metpy.calc`` module already implements and
maintains, numerically verified against the standard American
Meteorological Society Glossary definitions - ACF's own established
convention (see geospatial/distortion.py, crs_manager.py) is to build
on a reliable, actively-maintained library for physics infrastructure
like this rather than hand-roll a second parcel solver ACF would then
have to independently verify and maintain. This module is the
adaptation layer: it converts ACF's plain-float/array SoundingProfile
into the pint-quantity arrays MetPy's functions require, calls the
real MetPy computation, and converts the result back to ACF's usual
plain-SI-float convention - no formula is reimplemented here, only
wired up and unit-converted.

Reference:
    MetPy (Unidata); American Meteorological Society Glossary of
    Meteorology entries for CAPE, CIN, LFC, EL.
"""

from __future__ import annotations

from typing import Any

import metpy.calc as mpcalc
import numpy as np
from metpy.units import units as mp_units

from acf.science.radiosonde import SoundingProfile


def _profile_arrays(profile: SoundingProfile) -> tuple[Any, Any, Any]:
    """Convert a SoundingProfile's levels to the pint-quantity arrays MetPy expects."""
    pressure = np.array([lvl.pressure_hpa for lvl in profile.levels]) * mp_units.hPa
    temperature = np.array([lvl.temperature_c for lvl in profile.levels]) * mp_units.degC
    dewpoint = np.array([lvl.dewpoint_c for lvl in profile.levels]) * mp_units.degC
    return pressure, temperature, dewpoint


class ParcelAscentEngine:
    """
    Computes real parcel-ascent thermodynamics from a SoundingProfile.
    """

    @staticmethod
    def surface_parcel_profile_c(profile: SoundingProfile) -> list[float]:
        """
        Temperature (degC) of a surface parcel lifted dry-adiabatically
        to its LCL, then moist-adiabatically above it, evaluated at
        every pressure level of the profile.
        """
        pressure, temperature, dewpoint = _profile_arrays(profile)
        parcel_c = mpcalc.parcel_profile(pressure, temperature[0], dewpoint[0]).to("degC")
        return [float(v) for v in parcel_c.magnitude]

    @staticmethod
    def surface_based_cape_cin(profile: SoundingProfile) -> dict[str, float]:
        """Surface-based CAPE/CIN (J/kg): lift the lowest level's parcel through the full profile."""
        pressure, temperature, dewpoint = _profile_arrays(profile)
        cape, cin = mpcalc.surface_based_cape_cin(pressure, temperature, dewpoint)
        return {
            "cape_j_kg": float(cape.to("J/kg").magnitude),
            "cin_j_kg": float(cin.to("J/kg").magnitude),
        }

    @staticmethod
    def most_unstable_cape_cin(profile: SoundingProfile, depth_hpa: float = 300.0) -> dict[str, float]:
        """
        Most-unstable CAPE/CIN (J/kg): the parcel with the highest
        theta-e within the lowest `depth_hpa` of the profile is lifted,
        rather than assuming the surface parcel is always the most
        buoyant one (it often isn't, e.g. ahead of a warm front).
        """
        pressure, temperature, dewpoint = _profile_arrays(profile)
        mucape, mucin = mpcalc.most_unstable_cape_cin(
            pressure, temperature, dewpoint, depth=depth_hpa * mp_units.hPa
        )
        return {
            "mucape_j_kg": float(mucape.to("J/kg").magnitude),
            "mucin_j_kg": float(mucin.to("J/kg").magnitude),
        }

    @staticmethod
    def mixed_layer_cape_cin(profile: SoundingProfile, depth_hpa: float = 100.0) -> dict[str, float]:
        """
        Mixed-layer CAPE/CIN (J/kg): the parcel is the mean
        temperature/moisture of the lowest `depth_hpa` (representing a
        well-mixed boundary layer, e.g. by afternoon heating) rather
        than the single surface observation.
        """
        pressure, temperature, dewpoint = _profile_arrays(profile)
        mlcape, mlcin = mpcalc.mixed_layer_cape_cin(
            pressure, temperature, dewpoint, depth=depth_hpa * mp_units.hPa
        )
        return {
            "mlcape_j_kg": float(mlcape.to("J/kg").magnitude),
            "mlcin_j_kg": float(mlcin.to("J/kg").magnitude),
        }

    @staticmethod
    def lfc_and_el(profile: SoundingProfile) -> dict[str, float | None]:
        """
        Level of Free Convection (LFC) and Equilibrium Level (EL) for
        the surface-based parcel, as (pressure hPa, temperature degC)
        pairs. None where the parcel never becomes buoyant (no LFC/EL
        exists for this sounding) - MetPy itself returns NaN in that
        case, which is not silently coerced into a plausible-looking
        number here.
        """
        pressure, temperature, dewpoint = _profile_arrays(profile)
        lfc_p, lfc_t = mpcalc.lfc(pressure, temperature, dewpoint)
        el_p, el_t = mpcalc.el(pressure, temperature, dewpoint)

        def _or_none(q) -> float | None:
            v = float(q.magnitude)
            return None if np.isnan(v) else v

        return {
            "lfc_pressure_hpa": _or_none(lfc_p.to("hPa")),
            "lfc_temperature_c": _or_none(lfc_t.to("degC")),
            "el_pressure_hpa": _or_none(el_p.to("hPa")),
            "el_temperature_c": _or_none(el_t.to("degC")),
        }

    @staticmethod
    def severe_weather_indices(profile: SoundingProfile) -> dict[str, float]:
        """
        The classic suite of parcel-ascent-based severe-weather sounding
        indices: K-Index, Total Totals, Showalter Index, and the
        surface-based Lifted Index (needs the real parcel profile, unlike
        K-Index/Total Totals which only need environmental temperatures).
        """
        pressure, temperature, dewpoint = _profile_arrays(profile)
        parcel = mpcalc.parcel_profile(pressure, temperature[0], dewpoint[0])

        k_index = mpcalc.k_index(pressure, temperature, dewpoint)
        total_totals = mpcalc.total_totals_index(pressure, temperature, dewpoint)
        showalter = mpcalc.showalter_index(pressure, temperature, dewpoint)
        lifted = mpcalc.lifted_index(pressure, temperature, parcel)

        # K-Index is an absolute temperature (degC); Total Totals,
        # Showalter and the Lifted Index are temperature *differences*
        # (pint's "delta_degree_Celsius") - 1 delta_degC == 1 K, so the
        # magnitude is already the right numeric value without a unit
        # conversion (which would otherwise raise, since pint treats an
        # absolute-vs-delta Celsius conversion as dimensionally distinct).
        return {
            "k_index_c": float(k_index.to("degC").magnitude),
            "total_totals_c": float(total_totals.magnitude),
            "showalter_index_c": float(np.asarray(showalter.magnitude).reshape(-1)[0]),
            "lifted_index_c": float(np.asarray(lifted.magnitude).reshape(-1)[0]),
        }

    @classmethod
    def full_report(cls, profile: SoundingProfile) -> dict[str, Any]:
        """Convenience: every parcel-ascent diagnostic above, in one call."""
        report: dict[str, Any] = {}
        report.update(cls.surface_based_cape_cin(profile))
        report.update(cls.lfc_and_el(profile))
        try:
            report.update(cls.most_unstable_cape_cin(profile))
        except ValueError:
            pass  # profile doesn't span the requested search depth; omitted, not faked.
        try:
            report.update(cls.mixed_layer_cape_cin(profile))
        except ValueError:
            pass
        try:
            report.update(cls.severe_weather_indices(profile))
        except ValueError:
            pass  # profile doesn't span the levels these indices require (e.g. 850/700/500 hPa).
        return report
