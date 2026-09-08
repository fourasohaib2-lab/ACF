"""
Stability
=========

Single-import facade over ACF's existing, individually-tested
atmospheric stability indices — same pattern as thermodynamics.py and
moisture.py. No formulas are reimplemented here; this module only
aggregates.

Per ACF's single-source-of-truth rule, each index already has exactly
one canonical file:
    lcl.py                     (LCL, Espy fixed-rate + Bolton 1980)
    lifted_index.py             (LI)
    k_index.py                  (KI, George 1960)
    total_totals.py             (TT)
    sweat_index.py               (SWEAT, Miller 1972 — full term-
                                  clamping rules, verified against
                                  primary source)
    showalter_index.py           (SI, Showalter 1953)
    storm_relative_helicity.py   (SRH, single-layer + multi-layer
                                  profile per Davies-Jones et al. 1990)
    cape.py / cin.py             (CAPE/CIN, buoyancy integral)

MUCAPE / MLCAPE / SBCAPE / DCAPE
---------------------------------
MUCAPE (most-unstable), MLCAPE (mixed-layer) and SBCAPE (surface-
based) are NOT different formulas — they are CAPE.calculate() applied
to three different parcel definitions (which level's temperature/
humidity you feed in as the "parcel" profile). ACF does not duplicate
CAPE's implementation three times; callers select the parcel by
choosing which sounding level(s) to pass to CAPE.calculate() /
CIN.calculate(). See calculate_cape_for_parcel() below for the
selection convention this facade uses.

DCAPE (downdraft CAPE) is NOT implemented anywhere in ACF yet. It
requires simulating a moist-adiabatic descent of a parcel from a
specified level (typically the level of minimum theta-e, found via a
vertical profile) with environmental entrainment — genuinely different
physics from CAPE's ascent integral, and it needs the profile/moist-
adiabat-solver infrastructure that science/radiosonde.py is meant to
provide (not yet built, see /tmp/acf_integration_progress.md). Flagged
as a real, documented gap rather than approximated without a verified
formula.
"""

from typing import Literal

from acf.science.cape import CAPE
from acf.science.cin import CIN
from acf.science.k_index import KIndex
from acf.science.lcl import LCL
from acf.science.lifted_index import LiftedIndex
from acf.science.showalter_index import ShowalterIndex
from acf.science.storm_relative_helicity import StormRelativeHelicity
from acf.science.sweat_index import SWEATIndex
from acf.science.total_totals import TotalTotals

ParcelType = Literal["surface_based", "mixed_layer", "most_unstable"]


class Stability:
    """Aggregate facade for atmospheric stability calculations."""

    # --- Lifting condensation level ---------------------------------
    @staticmethod
    def lcl_height_espy(temperature_c: float, dewpoint_c: float) -> float:
        """LCL height (m), Espy fixed-rate approximation. See LCL.calculate()."""
        return LCL.calculate(temperature_c, dewpoint_c)

    @staticmethod
    def lcl_height_bolton(temperature_k: float, dewpoint_k: float) -> float:
        """LCL height (m), Bolton (1980)-based. See LCL.calculate_bolton()."""
        return LCL.calculate_bolton(temperature_k, dewpoint_k)

    # --- Simple stability indices ------------------------------------
    @staticmethod
    def lifted_index(parcel_temperature_500: float, environment_temperature_500: float) -> float:
        """LI (degC). See LiftedIndex.calculate()."""
        return LiftedIndex.calculate(parcel_temperature_500, environment_temperature_500)

    @staticmethod
    def showalter_index(parcel_temperature_500: float, environment_temperature_500: float) -> float:
        """SI (degC), Showalter 1953. See ShowalterIndex.calculate()."""
        return ShowalterIndex.calculate(parcel_temperature_500, environment_temperature_500)

    @staticmethod
    def k_index(t850: float, t700: float, t500: float, td850: float, td700: float) -> float:
        """KI, George 1960. See KIndex.calculate()."""
        return KIndex.calculate(t850, t700, t500, td850, td700)

    @staticmethod
    def total_totals(t850: float, td850: float, t500: float) -> float:
        """TT. See TotalTotals.calculate()."""
        return TotalTotals.calculate(t850, td850, t500)

    @staticmethod
    def sweat_index(
        td850: float, tt: float, wind850: float, wind500: float, dir850: float, dir500: float
    ) -> float:
        """SWEAT, Miller 1972 (full term-clamping rules). See SWEATIndex.calculate()."""
        return SWEATIndex.calculate(td850, tt, wind850, wind500, dir850, dir500)

    # --- Convective indices -------------------------------------------
    @staticmethod
    def calculate_cape_for_parcel(
        parcel_type: ParcelType,
        parcel_temperature: list[float],
        environment_temperature: list[float],
        height: list[float],
        **kwargs,
    ) -> float:
        """
        Compute CAPE for a given parcel-definition convention.

        Parameters
        ----------
        parcel_type : {"surface_based", "mixed_layer", "most_unstable"}
            Documents *which* parcel `parcel_temperature` represents —
            the caller is responsible for having already built that
            profile (surface parcel lifted, mixed-layer-averaged
            parcel lifted, or the most-unstable level's parcel lifted).
            This facade does not search a sounding for you (that needs
            science/radiosonde.py's SoundingProfile, not yet built).
        parcel_temperature, environment_temperature, height : list[float]
            Same as CAPE.calculate().
        **kwargs
            Forwarded to CAPE.calculate() (parcel_humidity,
            environment_humidity, is_kelvin).

        Returns
        -------
        float
            CAPE (J/kg) for the supplied parcel. The result is
            identical regardless of `parcel_type` — it exists purely
            for self-documenting call sites (e.g.
            calculate_cape_for_parcel("mixed_layer", ...) makes the
            caller's intent explicit and greppable).
        """
        if parcel_type not in ("surface_based", "mixed_layer", "most_unstable"):
            raise ValueError(f"unknown parcel_type: {parcel_type!r}")
        return CAPE.calculate(parcel_temperature, environment_temperature, height, **kwargs)

    @staticmethod
    def cin(
        parcel_temperature: list[float], environment_temperature: list[float], height: list[float], **kwargs
    ) -> float:
        """CIN (J/kg magnitude). See CIN.calculate()."""
        return CIN.calculate(parcel_temperature, environment_temperature, height, **kwargs)

    @staticmethod
    def storm_relative_helicity_layer(u: float, v: float, storm_u: float, storm_v: float, du: float, dv: float) -> float:
        """SRH for a single layer. See StormRelativeHelicity.calculate()."""
        return StormRelativeHelicity.calculate(u, v, storm_u, storm_v, du, dv)

    @staticmethod
    def storm_relative_helicity_profile(
        u: list[float], v: list[float], storm_u: float, storm_v: float
    ) -> float:
        """SRH over a full wind profile, Davies-Jones et al. (1990). See StormRelativeHelicity.calculate_profile()."""
        return StormRelativeHelicity.calculate_profile(u, v, storm_u, storm_v)
