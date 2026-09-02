"""
Real forecast time-metadata consistency checking.
"""

from datetime import datetime, timedelta

from acf.core.exceptions import TimeError


def check_forecast_time_ordering(
    forecast_reference_time: datetime, valid_time: datetime, max_lead_time: timedelta | None = None
) -> None:
    """
    Verify a forecast's time metadata is internally consistent.

    Parameters
    ----------
    forecast_reference_time : datetime
        When the model run started (the "run"/"cycle" time).
    valid_time : datetime
        The time this forecast is valid for.
    max_lead_time : timedelta, optional
        If given, also reject a lead_time longer than this - e.g. to
        catch an accidental year/unit mix-up producing a lead time of
        years instead of hours. Not checked by default (no universal
        "too long" a forecast can validly be).

    Raises
    ------
    TimeError
        If valid_time is before forecast_reference_time (a forecast
        cannot be valid for a time before its own model run started -
        that would mean a negative lead time), or if max_lead_time is
        given and exceeded.
    """
    if valid_time < forecast_reference_time:
        raise TimeError(
            f"valid_time ({valid_time}) is before forecast_reference_time "
            f"({forecast_reference_time}) - a forecast cannot be valid before its own run started "
            f"(negative lead time)"
        )

    if max_lead_time is not None:
        lead_time = valid_time - forecast_reference_time
        if lead_time > max_lead_time:
            raise TimeError(
                f"lead_time ({lead_time}) exceeds max_lead_time ({max_lead_time}) - "
                f"possible unit mix-up in valid_time or forecast_reference_time"
            )
