"""
ACF Complexity Engine — real METAR-based verification of the ceiling/visibility estimates
================================================================================================

Closes part of AWCI's verification gap (§42 of the cross-checked "AWCI
— programme complet" specification, post-model4d audit, 2026-09-12)
using data ALREADY live-connected in this codebase - real METAR
decoding (`acf.aviation.icao.metar_decoder`), the same real feed
`acf.gui.dashboard.awci_messages_panel` already pulls from the public
NOAA Aviation Weather Center API. No new external data source is
introduced here.

What this verifies, and what it does NOT
---------------------------------------------
`compare_estimated_ceiling_to_metar()` compares `acf.awci.ceiling.
compute_real_ceiling_at_point()`'s LCL-approximation estimate against
one real METAR's own reported ceiling (the real ICAO/FAA definition:
height AGL of the lowest BKN/OVC cloud layer, or vertical visibility if
the sky is obscured) - computed from that SAME METAR's own real surface
temperature/dewpoint/QNH, so a single real METAR report is entirely
self-sufficient (no separately-supplied NWP data needed).

`compare_estimated_visibility_risk_to_metar()` performs the companion
comparison for `acf.awci.visibility.compute_real_visibility_risk_at_point()`
- honestly NOT a numeric error metric like the ceiling comparison
above: the visibility module returns a [0, 1] risk PROXY, not a literal
distance (see that module's own honest-scope disclosure), so it is not
commensurable with a real METAR visibility in meters. This function
instead reports both real quantities side by side - the real risk
score and the real observed visibility, classified into the real
FAA/NOAA visibility-only flight category (`classify_visibility_category()`,
the companion of `acf.awci.ceiling.classify_ceiling_category()`) - for
the caller to judge consistency (e.g. does a real LIFR-visibility
report coincide with an elevated real risk score), rather than this
function asserting a false quantitative agreement.

This is a real, single point-in-time COMPARISON, never a calibration
or validation of the underlying formula: `acf.awci.ceiling`'s LCL
approximation remains scientific status HYPOTHESIS (see
`acf.awci.scientific_status`) regardless of how any one comparison
turns out. A real calibration/validation campaign would aggregate many
such comparisons across stations/seasons/conditions with real
statistics - see `acf.awci.calibration`/`acf.awci.forecaster_validation`
for that still-unexecuted infrastructure; this module produces one
real, honest data point such a campaign could consume, not the
campaign itself.

Real formula chain composed here, not reinvented
------------------------------------------------------
1. `acf.science.saturation_vapor_pressure.SaturationVaporPressure.calculate()`
   at the METAR's real dewpoint - the real vapor pressure AT dewpoint
   IS the real actual (not merely saturation) vapor pressure of the
   air, a standard meteorological identity (the same one
   `acf.science.dewpoint.DewPoint.calculate()` inverts).
2. `acf.science.saturation_mixing_ratio.SaturationMixingRatio.calculate()`
   - the same real w = 0.622*e/(p-e) formula, applied with the actual
   (not saturation) vapor pressure from step 1 - its derivation does
   not require `e` to specifically be a saturation value.
3. `q = w / (1 + w)` - the exact, definitional mixing-ratio-to-
   specific-humidity conversion (real, not an approximation).
4. `acf.awci.ceiling.compute_real_ceiling_at_point()` - already real,
   composed here with the real derived inputs above.

Real ceiling extraction from METAR
--------------------------------------
The real ICAO/FAA ceiling definition: height AGL of the lowest BKN or
OVC layer (`METARReport.cloud_layers`), or the real reported vertical
visibility (`METARReport.vertical_visibility_ft`) when the sky is
obscured - FEW/SCT layers do not count as a ceiling (real, standard
aviation convention). No BKN/OVC layer and no vertical visibility
reported is a real "no ceiling" (unlimited) condition, not a missing
observation.
"""

from __future__ import annotations

from typing import Any

from acf.aviation.icao.metar_decoder import METARReport
from acf.awci.ceiling import compute_real_ceiling_at_point
from acf.awci.visibility import compute_real_visibility_risk_at_point
from acf.science.saturation_mixing_ratio import SaturationMixingRatio
from acf.science.saturation_vapor_pressure import SaturationVaporPressure

_FT_TO_M = 0.3048

#: Real FAA/NOAA Aviation Weather Center visibility-only flight-
#: category thresholds (1/3/5 statute miles, converted to meters) -
#: the companion half of the real FAA flight-category convention
#: `acf.awci.ceiling`'s LIFR/IFR/MVFR/VFR ceiling-only thresholds
#: already implement (see that module's own docstring for why the two
#: halves are classified separately, never combined into one function).
LIFR_VISIBILITY_M = 1609.344
IFR_VISIBILITY_M = 4828.032
MVFR_VISIBILITY_M = 8046.72


def classify_visibility_category(visibility_m: float) -> str:
    """Real FAA/NOAA visibility-only category for a real observed visibility (m) - see module-level constants."""
    if visibility_m < LIFR_VISIBILITY_M:
        return "LIFR"
    if visibility_m < IFR_VISIBILITY_M:
        return "IFR"
    if visibility_m < MVFR_VISIBILITY_M:
        return "MVFR"
    return "VFR"


def extract_real_observed_ceiling_ft(report: METARReport) -> dict[str, Any]:
    """
    Real observed ceiling (feet AGL) from a real, already-decoded
    `METARReport` - see module docstring for the real ICAO/FAA
    definition this follows (lowest BKN/OVC layer, or vertical
    visibility if the sky is obscured).

    Returns
    -------
    dict
        ceiling_ft : real float, or `None` when no real ceiling was
            reported (an honest "unlimited ceiling" condition, never
            fabricated).
        ceiling_type : the real reported category ("BKN", "OVC",
            "INDEFINITE_VERTICAL_VISIBILITY", or "NO_CEILING_REPORTED").
        is_real_data, honest_limitation (when `ceiling_ft` is `None`).
    """
    if report.vertical_visibility_ft is not None:
        return {
            "ceiling_ft": float(report.vertical_visibility_ft),
            "ceiling_type": "INDEFINITE_VERTICAL_VISIBILITY",
            "is_real_data": True,
        }

    ceiling_layers = [layer for layer in report.cloud_layers if layer["coverage"] in ("BKN", "OVC")]
    if not ceiling_layers:
        return {
            "ceiling_ft": None,
            "ceiling_type": "NO_CEILING_REPORTED",
            "is_real_data": True,
            "honest_limitation": (
                "No real BKN/OVC layer and no real vertical visibility reported in this METAR - a real "
                "'unlimited ceiling' condition (e.g. CAVOK/SKC/FEW-only sky), not a missing observation."
            ),
        }

    lowest = min(ceiling_layers, key=lambda layer: layer["base_ft"])
    return {
        "ceiling_ft": float(lowest["base_ft"]),
        "ceiling_type": lowest["coverage"],
        "is_real_data": True,
    }


def specific_humidity_from_dewpoint(dewpoint_c: float, pressure_hpa: float) -> float:
    """
    Real specific humidity (kg/kg) from a real dewpoint and pressure -
    composes 2 already-real formulas (see module docstring), no new
    physics invented. Specific humidity depends on dewpoint and
    pressure alone - air temperature affects RELATIVE humidity, not
    specific humidity, at a fixed dewpoint/pressure, so it is not a
    parameter here.
    """
    vapor_pressure_hpa = SaturationVaporPressure.calculate(dewpoint_c, is_kelvin=False)
    mixing_ratio = SaturationMixingRatio.calculate(vapor_pressure_hpa, pressure_hpa)
    return mixing_ratio / (1.0 + mixing_ratio)


def compare_estimated_ceiling_to_metar(report: METARReport) -> dict[str, Any]:
    """
    Real, self-contained comparison of `acf.awci.ceiling`'s LCL-
    approximation estimate against one real METAR's own reported
    ceiling - see module docstring for the real formula chain and its
    honest scope (a single comparison, never a calibration/validation
    claim about the underlying formula).

    Parameters
    ----------
    report : METARReport
        A real, already-decoded METAR (e.g.
        `METARDecoder.decode(raw_text)`).

    Returns
    -------
    dict
        estimated_ceiling_m, observed_ceiling_m, error_m,
        absolute_error_m : real values, or `None` (never fabricated)
            when a real comparison cannot be made (missing real
            temperature/dewpoint/QNH, a non-positive real computed
            relative humidity, or no real ceiling reported).
        observed_ceiling_type : the real METAR ceiling category (see
            `extract_real_observed_ceiling_ft()`).
        status, is_real_data, honest_limitation.
    """
    if report.temperature_c is None or report.dewpoint_c is None or report.qnh_hpa is None:
        return {
            "estimated_ceiling_m": None,
            "observed_ceiling_m": None,
            "error_m": None,
            "absolute_error_m": None,
            "observed_ceiling_type": None,
            "status": "NOT_COMPARABLE_MISSING_REAL_METAR_FIELDS",
            "is_real_data": False,
            "honest_limitation": (
                "Real temperature, dewpoint, and QNH must all be present in this METAR to derive a real "
                "specific humidity and a real independent temperature for the comparison - at least one was "
                "honestly absent from this report (never substituted, e.g. temperature is never fabricated "
                "from dewpoint - that would force an artificial 100% relative humidity regardless of the "
                "real reported conditions)."
            ),
        }

    observed = extract_real_observed_ceiling_ft(report)
    if observed["ceiling_ft"] is None:
        return {
            "estimated_ceiling_m": None,
            "observed_ceiling_m": None,
            "error_m": None,
            "absolute_error_m": None,
            "observed_ceiling_type": observed["ceiling_type"],
            "status": "NOT_COMPARABLE_NO_REAL_CEILING_REPORTED",
            "is_real_data": False,
            "honest_limitation": observed.get(
                "honest_limitation", "No real ceiling reported in this METAR - nothing to compare against."
            ),
        }

    specific_humidity = specific_humidity_from_dewpoint(report.dewpoint_c, report.qnh_hpa)
    estimated = compute_real_ceiling_at_point(
        temperature_k=report.temperature_c + 273.15,
        specific_humidity=specific_humidity,
        pressure_hpa=report.qnh_hpa,
    )
    if not estimated["is_real_data"]:
        return {
            "estimated_ceiling_m": None,
            "observed_ceiling_m": observed["ceiling_ft"] * _FT_TO_M,
            "error_m": None,
            "absolute_error_m": None,
            "observed_ceiling_type": observed["ceiling_type"],
            "status": "NOT_COMPARABLE_ESTIMATE_UNDEFINED",
            "is_real_data": False,
            "honest_limitation": estimated["honest_limitation"],
        }

    observed_ceiling_m = observed["ceiling_ft"] * _FT_TO_M
    error_m = estimated["ceiling_height_m"] - observed_ceiling_m

    return {
        "estimated_ceiling_m": estimated["ceiling_height_m"],
        "observed_ceiling_m": observed_ceiling_m,
        "error_m": error_m,
        "absolute_error_m": abs(error_m),
        "observed_ceiling_type": observed["ceiling_type"],
        "status": "REAL_COMPARISON",
        "is_real_data": True,
        "honest_limitation": (
            "A real, single point-in-time comparison at this METAR's own station - not a calibration or "
            "validation of acf.awci.ceiling's LCL approximation (still scientific status HYPOTHESIS "
            "regardless of this result). A real campaign would aggregate many such comparisons across "
            "stations/seasons/conditions (see acf.awci.forecaster_validation/calibration for that "
            "still-unexecuted infrastructure)."
        ),
    }


def compare_estimated_visibility_risk_to_metar(report: METARReport) -> dict[str, Any]:
    """
    Real, self-contained comparison of `acf.awci.visibility`'s [0, 1]
    risk proxy against one real METAR's own reported visibility - see
    module docstring for why this is a side-by-side comparison, NOT a
    numeric error metric (the proxy and a real distance in meters are
    not commensurable).

    Honest limitation carried over from `acf.awci.visibility`'s own
    scope: `precipitation_mm_h` is passed as `0.0` here - this function
    does not attempt to convert a METAR's real present-weather codes
    (e.g. "+RA"/"-SN") into a real quantitative rate, which would need
    its own real, cited intensity mapping this codebase does not have
    (the same limitation already disclosed for `acf.awci.spatial_field`'s
    own `compute_visibility` integration) - only the real relative-
    humidity/fog-proximity half of the risk proxy is exercised here.

    Parameters
    ----------
    report : METARReport
        A real, already-decoded METAR.

    Returns
    -------
    dict
        visibility_risk_score, fog_proximity : the real risk proxy and
            its real intermediate signal (see
            `acf.awci.visibility.compute_real_visibility_risk_at_point()`),
            or `None` when not comparable.
        observed_visibility_m : the real METAR-reported visibility (m),
            or `None`.
        observed_visibility_category : the real FAA/NOAA visibility-
            only category (`classify_visibility_category()`), or
            `None`.
        status, is_real_data, honest_limitation.
    """
    if report.temperature_c is None or report.dewpoint_c is None or report.qnh_hpa is None:
        return {
            "visibility_risk_score": None,
            "fog_proximity": None,
            "observed_visibility_m": None,
            "observed_visibility_category": None,
            "status": "NOT_COMPARABLE_MISSING_REAL_METAR_FIELDS",
            "is_real_data": False,
            "honest_limitation": (
                "Real temperature, dewpoint, and QNH must all be present in this METAR to derive a real "
                "specific humidity and compare - at least one was honestly absent from this report."
            ),
        }

    if report.visibility_m is None:
        return {
            "visibility_risk_score": None,
            "fog_proximity": None,
            "observed_visibility_m": None,
            "observed_visibility_category": None,
            "status": "NOT_COMPARABLE_NO_REAL_VISIBILITY_REPORTED",
            "is_real_data": False,
            "honest_limitation": "No real visibility group was present in this METAR - nothing to compare against.",
        }

    specific_humidity = specific_humidity_from_dewpoint(report.dewpoint_c, report.qnh_hpa)
    risk = compute_real_visibility_risk_at_point(
        temperature_k=report.temperature_c + 273.15,
        specific_humidity=specific_humidity,
        pressure_hpa=report.qnh_hpa,
        precipitation_mm_h=0.0,
    )
    if not risk["is_real_data"]:
        return {
            "visibility_risk_score": None,
            "fog_proximity": None,
            "observed_visibility_m": report.visibility_m,
            "observed_visibility_category": classify_visibility_category(report.visibility_m),
            "status": "NOT_COMPARABLE_ESTIMATE_UNDEFINED",
            "is_real_data": False,
            "honest_limitation": risk["honest_limitation"],
        }

    return {
        "visibility_risk_score": risk["visibility_risk_score"],
        "fog_proximity": risk["fog_proximity"],
        "observed_visibility_m": report.visibility_m,
        "observed_visibility_category": classify_visibility_category(report.visibility_m),
        "status": "REAL_COMPARISON",
        "is_real_data": True,
        "honest_limitation": (
            "A real side-by-side comparison, not a numeric error metric - acf.awci.visibility's [0, 1] risk "
            "proxy and a real visibility in meters are not commensurable (see module docstring). "
            "precipitation_mm_h=0.0 throughout (no real present-weather-to-rate mapping here), so only the "
            "real fog-proximity half of the proxy is exercised. Not a calibration or validation of the "
            "underlying proxy (still scientific status HYPOTHESIS regardless of this result)."
        ),
    }
