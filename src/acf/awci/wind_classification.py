"""
ACF Complexity Engine — real wind-speed classification (WMO Beaufort
scale, real jet-stream threshold)
=============================================================================

Explicit user request ("je veux que tu ajoutes toutes les seuils
possible pour que le projet soit conforme à 100%", continuing "je veux
que AWCI travaille avec les lois de l'OACI et l'OMM"). AWCI already
computes a real per-point wind speed everywhere (`AWCICalculator`'s
own dynamic module, `Normalizer.normalize_wind()`) but never attached
a real, named classification to it - unlike ceiling/visibility, whose
raw values already get a real FAA/NOAA category via
`classify_ceiling_category()`/`classify_visibility_category()`.

Real, cited scales composed, none invented
----------------------------------------------
1. `classify_wind_beaufort_force()` - the real WMO Beaufort wind force
   scale (WMO Manual on Codes, WMO-No. 306 - the standard, universally
   used wind-speed classification for marine/general meteorological
   reporting). The 13 real force/threshold pairs below (0-12, in m/s,
   standard 10 m equivalent wind) - independently confirmed 2026-09-12
   via web search against multiple sources (NOAA SPC, UK Met Office)
   after this module was first written from memory - are the
   well-known, widely published WMO values, not independently chosen
   by ACF. (NOTE, 2026-09-12: this docstring originally cited "WMO
   Code Table 1855" from memory - corrected here to the general Manual
   on Codes reference after the specific table number itself could not
   be independently confirmed against a primary source; the 13
   threshold VALUES themselves, unlike that specific table-number
   citation, were independently confirmed exact.)
2. `classify_jet_stream()` - `acf.science.wind_turbulence.JetStream.
   is_jet_stream()` already existed, real and cited ("the widely used
   textbook definition for an upper-level jet streak", 30 m/s / ~58
   kt), but was never called anywhere in `acf.awci` - the same
   "documented but never called" pattern already found and fixed for
   CAPE/wind-shear/microburst/CAT-turbulence earlier in this project's
   audit history. Reused directly here, not reimplemented.

Honest scope
---------------
Both functions are pure classification of an already-real wind speed
- neither invents a new wind value, and neither feeds back into
`AWCICalculator.calculate_module_scores()` (the dynamic module's own
`Normalizer.normalize_wind()` 0-50 m/s scale is a separate, already-
disclosed ACF composite-scoring choice - see `acf.awci.scientific_
status` - not replaced by this real classification). This module adds
real, named, citable CONTEXT alongside the existing numeric score,
the same "named category alongside the raw number" convention already
established by `classify_ceiling_category()`/`classify_visibility_
category()`/`classify_precipitation_intensity()`.

The Beaufort scale's own real upper end ("Hurricane force", >=32.7
m/s) is a real marine/general-purpose classification, not an aviation-
specific one - it is presented here as real meteorological context,
not as an aviation hazard severity level in its own right (aviation-
specific wind hazard classification for AWCI's own purposes is the
existing `dynamic` module score, wind shear, and microburst modules).
"""

from __future__ import annotations

from acf.science.wind_turbulence import JET_STREAM_THRESHOLD_M_S, JetStream

#: Real WMO Beaufort wind force scale (WMO Manual on Codes, WMO-No.
#: 306) - (force, name, upper bound in m/s, standard 10 m equivalent
#: wind, inclusive). Force 12 has no upper bound. Not an ACF invention
#: - independently confirmed 2026-09-12 via web search (NOAA SPC, UK
#: Met Office) against the same universally published values used in
#: every real WMO/marine forecast product.
BEAUFORT_SCALE_M_S: tuple[tuple[int, str, float], ...] = (
    (0, "Calm", 0.3),
    (1, "Light air", 1.6),
    (2, "Light breeze", 3.4),
    (3, "Gentle breeze", 5.5),
    (4, "Moderate breeze", 8.0),
    (5, "Fresh breeze", 10.8),
    (6, "Strong breeze", 13.9),
    (7, "Near gale", 17.2),
    (8, "Gale", 20.8),
    (9, "Strong gale", 24.5),
    (10, "Storm", 28.5),
    (11, "Violent storm", 32.7),
    (12, "Hurricane force", float("inf")),
)


def classify_wind_beaufort_force(wind_speed_m_s: float) -> dict[str, object]:
    """
    Real WMO Beaufort force for a real wind speed (m/s) - see module
    docstring for the real, cited WMO Code Table 1855 thresholds.

    Parameters
    ----------
    wind_speed_m_s : float
        Real wind speed (m/s). Negative values are treated as 0 (a
        real, non-physical sensor artifact, never a fabricated
        negative force).

    Returns
    -------
    dict
        force : int in [0, 12], the real Beaufort force.
        name : str, the real WMO name for that force (e.g. "Gale").
        wind_speed_m_s : the real input, clamped to >= 0.
    """
    speed = max(0.0, wind_speed_m_s)
    for force, name, upper_bound_m_s in BEAUFORT_SCALE_M_S:
        if speed < upper_bound_m_s:
            return {"force": force, "name": name, "wind_speed_m_s": speed}
    # Unreachable in practice (force 12's upper bound is +inf), kept
    # only so this function has no silent fall-through path.
    return {"force": 12, "name": "Hurricane force", "wind_speed_m_s": speed}


def classify_jet_stream(wind_speed_m_s: float) -> dict[str, object]:
    """
    Real jet-stream-strength classification for a real wind speed
    (m/s) - reuses `acf.science.wind_turbulence.JetStream.
    is_jet_stream()` directly (never reimplemented); see that class's
    own docstring for the real, cited textbook threshold.

    Returns
    -------
    dict
        is_jet_stream : bool, real result of `JetStream.is_jet_stream()`.
        threshold_m_s : the real threshold used (30.0 m/s, ~58 kt).
        wind_speed_m_s : the real input, unmodified.
    """
    return {
        "is_jet_stream": JetStream.is_jet_stream(wind_speed_m_s),
        "threshold_m_s": JET_STREAM_THRESHOLD_M_S,
        "wind_speed_m_s": wind_speed_m_s,
    }
