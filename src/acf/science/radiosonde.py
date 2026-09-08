"""
Radiosonde
==========

SoundingProfile: a vertical atmospheric profile data structure with
log-pressure interpolation and derived-quantity/index computation,
built entirely on top of ACF's existing, individually-verified
science/ modules (LCL, potential/equivalent-potential temperature,
moisture, KI/TT stability indices) — no formulas are reimplemented
here, only assembled and applied to real profile data.

NOTE: CAPE/CIN are NOT computed from a SoundingProfile here. Doing so
correctly requires simulating a parcel's dry- then moist-adiabatic
ascent from a chosen starting level (surface/mixed-layer/most-unstable)
through the environment — a genuine parcel-ascent model, which used to
be a separate, larger piece of infrastructure ACF didn't have
(distinct from CAPE.calculate()'s buoyancy integral, which already
assumes you hand it a parcel temperature trace). Naively feeding the
environmental temperature trace itself as the "parcel" would silently
give CAPE=0 always (no buoyancy difference) — flagged as a real gap
rather than producing a technically-callable but physically wrong
result.

UPDATE: that gap is now filled — see
acf.science.parcel_ascent.ParcelAscentEngine, which takes a
SoundingProfile (this class) and computes real surface-based/
most-unstable/mixed-layer CAPE/CIN, LFC/EL, and the parcel-dependent
severe-weather indices (Showalter, Lifted Index) via a genuine
MetPy-backed parcel ascent. Not merged into this class directly to
avoid a circular import (parcel_ascent.py imports SoundingProfile from
here); call it separately on a SoundingProfile instance.

Also implements precipitable water (PWAT), a simple, standard
integral not requiring external verification: PWAT (mm) =
(1/g) * integral(q dp), since 1 kg/m^2 of water column mass is by
definition equivalent to 1 mm of liquid depth (rho_water = 1000 kg/m^3).

Reference:
    Standard atmospheric sounding analysis, e.g. Holton & Hakim (2012).
"""

from dataclasses import dataclass
from math import log

from acf.science.constants import G, T0
from acf.science.equivalent_potential_temperature import EquivalentPotentialTemperature
from acf.science.lcl import LCL
from acf.science.moisture import Moisture
from acf.science.potential_temperature import PotentialTemperature
from acf.science.stability import Stability


@dataclass
class SoundingLevel:
    """One level of a vertical sounding."""

    pressure_hpa: float
    height_m: float
    temperature_c: float
    dewpoint_c: float
    wind_speed_m_s: float | None = None
    wind_direction_deg: float | None = None


class SoundingProfile:
    """A full vertical sounding (radiosonde-style) with derived analysis."""

    def __init__(self, levels: list[SoundingLevel]):
        """
        Parameters
        ----------
        levels : list of SoundingLevel
            Must be sorted surface-to-top (strictly decreasing pressure),
            at least 2 levels.

        Raises
        ------
        ValueError
            If fewer than 2 levels, or pressure is not strictly
            decreasing (surface to top).
        """
        if len(levels) < 2:
            raise ValueError("at least two levels are required.")
        for i in range(len(levels) - 1):
            if levels[i].pressure_hpa <= levels[i + 1].pressure_hpa:
                raise ValueError("levels must be sorted surface-to-top with strictly decreasing pressure.")
        self.levels = levels

    def interpolate_at_pressure(self, pressure_hpa: float) -> SoundingLevel:
        """
        Interpolate temperature/dewpoint/height linearly in log-pressure
        (the standard convention for atmospheric vertical interpolation)
        at an arbitrary pressure level. Wind is interpolated linearly
        (not log-p) since it isn't a thermodynamic quantity.

        Parameters
        ----------
        pressure_hpa : float
            Target pressure (hPa). Must be within the profile's range.

        Returns
        -------
        SoundingLevel
            Interpolated level.

        Raises
        ------
        ValueError
            If pressure_hpa is outside the profile's pressure range.
        """
        levels = self.levels
        if pressure_hpa > levels[0].pressure_hpa or pressure_hpa < levels[-1].pressure_hpa:
            raise ValueError(
                f"pressure_hpa={pressure_hpa} is outside the profile range "
                f"[{levels[-1].pressure_hpa}, {levels[0].pressure_hpa}]."
            )

        for i in range(len(levels) - 1):
            p_above, p_below = levels[i].pressure_hpa, levels[i + 1].pressure_hpa
            if p_below <= pressure_hpa <= p_above:
                if pressure_hpa == p_above:
                    return levels[i]
                if pressure_hpa == p_below:
                    return levels[i + 1]

                # Linear-in-log-pressure interpolation fraction.
                frac = log(p_above / pressure_hpa) / log(p_above / p_below)

                def lerp(a: float, b: float) -> float:
                    return a + frac * (b - a)

                wind_speed = None
                ws_above, ws_below = levels[i].wind_speed_m_s, levels[i + 1].wind_speed_m_s
                if ws_above is not None and ws_below is not None:
                    wind_speed = lerp(ws_above, ws_below)
                wind_dir = None
                wd_above, wd_below = levels[i].wind_direction_deg, levels[i + 1].wind_direction_deg
                if wd_above is not None and wd_below is not None:
                    wind_dir = lerp(wd_above, wd_below)

                return SoundingLevel(
                    pressure_hpa=pressure_hpa,
                    height_m=lerp(levels[i].height_m, levels[i + 1].height_m),
                    temperature_c=lerp(levels[i].temperature_c, levels[i + 1].temperature_c),
                    dewpoint_c=lerp(levels[i].dewpoint_c, levels[i + 1].dewpoint_c),
                    wind_speed_m_s=wind_speed,
                    wind_direction_deg=wind_dir,
                )

        raise ValueError(f"pressure_hpa={pressure_hpa} could not be bracketed (unexpected).")

    def potential_temperature_profile(self) -> list[float]:
        """theta (K) at every level, via PotentialTemperature (existing, verified)."""
        return [
            PotentialTemperature.calculate(lvl.temperature_c + T0, lvl.pressure_hpa) for lvl in self.levels
        ]

    def equivalent_potential_temperature_profile(self) -> list[float]:
        """theta_e (K) at every level, via Bolton (1980) (existing, verified)."""
        return [
            EquivalentPotentialTemperature.calculate_bolton_1980(
                lvl.temperature_c + T0, lvl.dewpoint_c + T0, lvl.pressure_hpa
            )
            for lvl in self.levels
        ]

    def relative_humidity_profile(self) -> list[float]:
        """RH (0-1) at every level, via Moisture (existing, verified)."""
        rh = []
        for lvl in self.levels:
            es = Moisture.saturation_vapor_pressure(lvl.temperature_c + T0, is_kelvin=True)
            e = Moisture.saturation_vapor_pressure(lvl.dewpoint_c + T0, is_kelvin=True)
            rh.append(Moisture.relative_humidity(e, es))
        return rh

    def mixing_ratio_profile(self) -> list[float]:
        """Mixing ratio r (kg/kg) at every level, via Moisture (existing, verified)."""
        r = []
        for lvl in self.levels:
            e = Moisture.saturation_vapor_pressure(lvl.dewpoint_c + T0, is_kelvin=True)
            r.append(Moisture.saturation_mixing_ratio(e, lvl.pressure_hpa))
        return r

    def precipitable_water_mm(self) -> float:
        """
        PWAT = (1/g) * integral(q dp), trapezoidal integration over the
        full profile.

        Returns
        -------
        float
            Precipitable water (mm).
        """
        mixing_ratios = self.mixing_ratio_profile()
        # Specific humidity q ~ r/(1+r); close enough to r for the small
        # values involved that using r directly (as many operational
        # PWAT implementations do) introduces negligible error, but we
        # convert properly since Moisture doesn't need q vs r fudged.
        specific_humidities = [r / (1.0 + r) for r in mixing_ratios]

        pwat_pa_kg_kg = 0.0
        for i in range(len(self.levels) - 1):
            dp_pa = (self.levels[i].pressure_hpa - self.levels[i + 1].pressure_hpa) * 100.0
            avg_q = 0.5 * (specific_humidities[i] + specific_humidities[i + 1])
            pwat_pa_kg_kg += avg_q * dp_pa

        return pwat_pa_kg_kg / G  # kg/m^2 == mm

    def surface_based_parcel_indices(self) -> dict:
        """
        Compute the standard suite of surface-based stability indices
        from this profile, by feeding it into the existing (already
        verified/tested) science/ modules. Uses the surface parcel
        lifted through the full profile for CAPE/CIN (a simplification:
        assumes the parcel follows the environmental temperature trace
        rather than a true moist/dry adiabatic ascent path — a full
        parcel-ascent model is a separate, larger undertaking not
        built yet; flagged rather than silently assumed exact).

        Returns
        -------
        dict
            {
                "lcl_height_m": float,
                "surface_theta_e_k": float,
                "precipitable_water_mm": float,
                "k_index": float (if 850/700/500 hPa levels are present),
                "total_totals": float (if 850/500 hPa levels are present),
            }
        """
        surface = self.levels[0]
        result: dict = {
            "lcl_height_m": LCL.calculate_bolton_celsius(surface.temperature_c, surface.dewpoint_c),
            "surface_theta_e_k": EquivalentPotentialTemperature.calculate_bolton_1980(
                surface.temperature_c + T0, surface.dewpoint_c + T0, surface.pressure_hpa
            ),
            "precipitable_water_mm": self.precipitable_water_mm(),
        }

        try:
            l850 = self.interpolate_at_pressure(850.0)
            l700 = self.interpolate_at_pressure(700.0)
            l500 = self.interpolate_at_pressure(500.0)
            result["k_index"] = Stability.k_index(
                t850=l850.temperature_c,
                t700=l700.temperature_c,
                t500=l500.temperature_c,
                td850=l850.dewpoint_c,
                td700=l700.dewpoint_c,
            )
            result["total_totals"] = Stability.total_totals(
                t850=l850.temperature_c, td850=l850.dewpoint_c, t500=l500.temperature_c
            )
        except ValueError:
            pass  # profile doesn't span the required levels; indices omitted, not faked.

        return result
