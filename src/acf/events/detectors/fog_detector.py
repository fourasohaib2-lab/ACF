"""
Real fog-favorable-condition detection.

Honest naming: this detects the real thermodynamic PRECONDITION for
radiation fog (near-saturated air + calm wind), computed from real
temperature/humidity/pressure/wind via a genuine MetPy calculation -
NOT confirmed fog (a visibility reduction). No visibility or liquid
water content field exists anywhere in ACF's real solver output to
confirm actual fog has formed; event.type is "fog_favorable_conditions",
not "fog", so a consumer never mistakes a precondition for a
confirmed observation.
"""

from datetime import datetime
from typing import Any

import metpy.calc as mpcalc
import numpy as np
from metpy.units import units as mp_units

from acf.core.contracts.provenance import Provenance
from acf.events.event import Event

#: ACF's own operational design choice, documented not hidden (same
#: convention as acf.awci's own thresholds): near-saturation and calm
#: wind are the real, textbook thermodynamic precondition for
#: radiation fog to form, not an arbitrary pair of numbers.
DEFAULT_RH_THRESHOLD_PCT = 95.0
DEFAULT_WIND_THRESHOLD_M_S = 2.0


def detect_fog_favorable_events(
    temperature_field: Any,
    specific_humidity_field: Any,
    pressure_field_hpa: Any,
    wind_speed_field: Any,
    lats: Any,
    lons: Any,
    model: str,
    rh_threshold_pct: float = DEFAULT_RH_THRESHOLD_PCT,
    wind_threshold_m_s: float = DEFAULT_WIND_THRESHOLD_M_S,
    valid_time: datetime | None = None,
) -> list[Event]:
    """
    Detect real fog-favorable conditions: relative humidity (computed
    via a genuine MetPy calculation from real specific humidity,
    temperature and pressure - not measured or assumed directly) at or
    above `rh_threshold_pct`, AND wind speed at or below
    `wind_threshold_m_s` (calm conditions let radiative cooling
    saturate the near-surface layer - the real physical mechanism, not
    an arbitrary AND).

    Parameters
    ----------
    temperature_field, specific_humidity_field, pressure_field_hpa,
    wind_speed_field : array-like, shape (n_lat, n_lon)
        Real fields, e.g. acf.awci.spatial_field.
        compute_real_complexity_field()'s own *_field outputs
        (genuine CoupledEarthSolver output).
    lats, lons : 1D real coordinate arrays.
    model : str
        Recorded as the event's supporting_models.

    Returns
    -------
    list[Event]
        type="fog_favorable_conditions" (see module docstring for why
        not "fog"). intensity is the real computed relative humidity
        in %, clamped to [0, 100] for reporting - MetPy's formula can
        nominally exceed 100% for near-/super-saturated or extrapolated
        inputs (verified empirically); the real unclamped value is also
        kept in supporting_parameters["relative_humidity_pct_raw"] so
        nothing is hidden, only the headline `intensity` is bounded.
        Same probability=1.0/confidence=0.5 convention as
        detect_strong_wind_events() - see its own docstring for why.
    """
    temperature = np.asarray(temperature_field)
    specific_humidity = np.asarray(specific_humidity_field)
    pressure_hpa = np.asarray(pressure_field_hpa)
    wind_speed = np.asarray(wind_speed_field)
    lats_arr = np.asarray(lats)
    lons_arr = np.asarray(lons)
    when = valid_time or datetime.now()

    relative_humidity_pct = (
        mpcalc.relative_humidity_from_specific_humidity(
            pressure_hpa * mp_units.hPa,
            temperature * mp_units.K,
            specific_humidity * mp_units("kg/kg"),
        )
        .to("percent")
        .magnitude
    )

    events = []
    for i in range(temperature.shape[0]):
        for j in range(temperature.shape[1]):
            rh_raw = float(relative_humidity_pct[i, j])
            wind = float(wind_speed[i, j])
            if rh_raw >= rh_threshold_pct and wind <= wind_threshold_m_s:
                events.append(
                    Event(
                        type="fog_favorable_conditions",
                        geometry={"lat": float(lats_arr[i]), "lon": float(lons_arr[j])},
                        start_time=when,
                        intensity=min(100.0, max(0.0, rh_raw)),
                        probability=1.0,
                        confidence=0.5,
                        supporting_parameters={
                            "relative_humidity_pct_raw": rh_raw,
                            "wind_speed_m_s": wind,
                            "rh_threshold_pct": rh_threshold_pct,
                            "wind_threshold_m_s": wind_threshold_m_s,
                        },
                        supporting_models=(model,),
                        provenance=Provenance(
                            generator="acf.events.detectors.fog_detector.detect_fog_favorable_events",
                            algorithm_version=f"rh>={rh_threshold_pct}%,wind<={wind_threshold_m_s}m/s",
                            notes="Detects the thermodynamic precondition for radiation fog, not confirmed "
                            "fog (no visibility field exists in ACF's real solver output).",
                        ),
                    )
                )
    return events
