"""
Real strong-wind event detection from a real wind speed field.
"""

from datetime import datetime
from typing import Any

import numpy as np

from acf.core.contracts.provenance import Provenance
from acf.events.event import Event

#: ACF's own operational design choice (~72 km/h) - matching common
#: real "strong wind warning" thresholds used operationally, not a
#: claim of one specific international standard. Documented, not
#: hidden, same disclosure convention as acf.awci's own weights.
DEFAULT_THRESHOLD_M_S = 20.0


def detect_strong_wind_events(
    wind_speed_field: Any,
    lats: Any,
    lons: Any,
    model: str,
    threshold_m_s: float = DEFAULT_THRESHOLD_M_S,
    valid_time: datetime | None = None,
) -> list[Event]:
    """
    Detect real strong-wind events: every grid point whose real wind
    speed meets or exceeds `threshold_m_s`.

    Parameters
    ----------
    wind_speed_field : array-like, shape (n_lat, n_lon)
        Real wind speed in m/s - e.g.
        acf.awci.spatial_field.compute_real_complexity_field()'s own
        wind_speed_field (genuine CoupledEarthSolver output, not
        synthetic).
    lats, lons : 1D real coordinate arrays matching wind_speed_field's shape.
    model : str
        Which model/configuration produced `wind_speed_field`, e.g.
        "ARPEGE" - recorded as the event's supporting_models.
    threshold_m_s : float
        See DEFAULT_THRESHOLD_M_S's own disclosure.
    valid_time : datetime, optional
        Defaults to now() if not given.

    Returns
    -------
    list[Event]
        One Event per grid point at or above threshold - probability=1.0
        (the real field genuinely met the threshold at that point in
        this one deterministic run - NOT a forecast probability across
        an ensemble, which this detector has no ensemble data for),
        confidence=0.5 (ACF's own conservative default for a single
        deterministic run with no ensemble/multi-model/observational
        corroboration - see acf.awci.calculator's own ensemble_spread/
        model_disagreement modules for how real corroboration would
        raise this, if a caller wires that data in separately).
    """
    field = np.asarray(wind_speed_field)
    lats_arr = np.asarray(lats)
    lons_arr = np.asarray(lons)
    when = valid_time or datetime.now()

    events = []
    for i in range(field.shape[0]):
        for j in range(field.shape[1]):
            speed = float(field[i, j])
            if speed >= threshold_m_s:
                events.append(
                    Event(
                        type="strong_wind",
                        geometry={"lat": float(lats_arr[i]), "lon": float(lons_arr[j])},
                        start_time=when,
                        intensity=speed,
                        probability=1.0,
                        confidence=0.5,
                        supporting_parameters={"wind_speed_m_s": speed, "threshold_m_s": threshold_m_s},
                        supporting_models=(model,),
                        provenance=Provenance(
                            generator="acf.events.detectors.wind_detector.detect_strong_wind_events",
                            algorithm_version=f"threshold={threshold_m_s}m/s",
                        ),
                    )
                )
    return events
