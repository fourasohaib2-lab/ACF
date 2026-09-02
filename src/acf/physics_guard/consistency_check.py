"""
Real cross-variable physical relationship checking.

Each check here is a genuine, uncontroversial thermodynamic/physical
identity - not a statistical heuristic or an ACF-specific design
choice (unlike acf.awci/acf.fire_weather's composite scoring weights,
which ARE documented as ACF's own choice).
"""

from acf.core.exceptions import ScientificConsistencyError


def check_dewpoint_not_above_temperature(temperature_k: float, dewpoint_k: float) -> None:
    """
    Real physical invariant: dew point can never exceed air temperature
    (dew point is, by definition, the temperature at which air would
    need to be cooled - at constant pressure and moisture content - to
    reach saturation; air that is already saturated has dew point equal
    to temperature, never above it).

    Raises
    ------
    ScientificConsistencyError
        If dewpoint_k > temperature_k - a genuine physical
        impossibility, not a borderline/uncertain case.
    """
    if dewpoint_k > temperature_k:
        raise ScientificConsistencyError(
            f"Dew point ({dewpoint_k} K) exceeds air temperature ({temperature_k} K) - "
            f"physically impossible (dew point is capped at air temperature by definition)"
        )


def check_relative_humidity_bounds(relative_humidity_pct: float) -> None:
    """
    Real physical invariant: relative humidity is a percentage of
    saturation and cannot be negative. (Values slightly above 100% can
    occur transiently in real supersaturated conditions - e.g. cloud
    formation - so this only rejects clearly invalid negative values or
    values far enough above 100% to indicate a real data/unit error,
    not genuine supersaturation.)

    Raises
    ------
    ScientificConsistencyError
        If relative_humidity_pct < 0, or > 110 (a supersaturation
        margin, not a hard 100% cutoff - documented above).
    """
    if relative_humidity_pct < 0.0:
        raise ScientificConsistencyError(f"Relative humidity ({relative_humidity_pct}%) cannot be negative")
    if relative_humidity_pct > 110.0:
        raise ScientificConsistencyError(
            f"Relative humidity ({relative_humidity_pct}%) is far enough above 100% to indicate "
            f"a data/unit error rather than genuine supersaturation (allowed up to 110%)"
        )
