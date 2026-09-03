"""
ACF's own documented operational sanity bounds - real range checking.

Honest disclosure (same convention as acf.awci.normalizer/
acf.fire_weather.normalizer): the bounds below are ACF's own
operational design choice for catching obviously-wrong values (unit
mix-ups, corrupted data, a decoding bug) - NOT a claim about the
absolute physical limits of the atmosphere anywhere on Earth (e.g. the
real atmosphere gets much colder than this module's lower temperature
bound, in the mesosphere/thermosphere - ACF's own domain today is
tropospheric NWP, so the bound is set generously wide for THAT domain,
not for exotic upper-atmosphere physics ACF doesn't model).
"""

from typing import Any

from acf.core.exceptions import RangeError
from acf.normalization.units import convert_unit
from acf.normalization.variable_names import cf_canonical_unit

#: (min, max) in the variable's real CF canonical unit (see
#: acf.normalization.variable_names.cf_canonical_unit() - these are the
#: same units resources/standards/cf/cf_standard_names.json declares,
#: not independently invented here).
OPERATIONAL_RANGES: dict[str, tuple[float, float]] = {
    # -100 degC to +60 degC - far wider than any real recorded surface
    # extreme (-89.2 degC Vostok, +56.7 degC Death Valley), generous on
    # purpose to only catch clearly-wrong values (e.g. a Celsius value
    # mistakenly treated as Kelvin), not to flag genuinely extreme
    # real weather.
    "air_temperature": (173.15, 333.15),
    # Same generous bound as air_temperature above - a dewpoint this
    # extreme would already be a data/decoding error regardless of the
    # separate, stricter real physical relationship (dewpoint cannot
    # exceed air temperature) that
    # acf.physics_guard.consistency_check.check_dewpoint_not_above_temperature()
    # checks instead. Added for acf.physics_guard.variable_quality's
    # real per-variable range check on dewpoint, previously undocumented.
    # Key spelled "dewpoint_temperature" (no underscore between "dew"
    # and "point"), NOT the strict CF Conventions spelling
    # "dew_point_temperature" - matches this project's own
    # already-established internal key throughout acf.physics_guard
    # (consistency_check.py/guard.py, both predating this entry), kept
    # consistent rather than silently "corrected" to true CF spelling.
    "dewpoint_temperature": (173.15, 333.15),
    # 10 hPa (extreme high-altitude / low-pressure system core) to
    # 1085 hPa (highest sea-level pressure ever recorded is ~1084 hPa).
    "air_pressure": (1000.0, 108500.0),
    # +/- 150 m/s - far above any recorded surface wind gust
    # (~113 m/s, Barrow Island 1996), generous for jet-stream-level winds.
    "eastward_wind": (-150.0, 150.0),
    "northward_wind": (-150.0, 150.0),
    # Scalar wind speed magnitude (e.g. METAR-reported surface wind
    # speed) - the non-negative counterpart to eastward_wind/
    # northward_wind above, same generous 150 m/s ceiling, but never
    # negative (a real reported speed can't be, unlike a signed vector
    # component).
    "wind_speed": (0.0, 150.0),
    "relative_humidity": (0.0, 100.0),
    # 0 to 40 g/kg - saturation specific humidity at very warm, very
    # humid tropical surface conditions is well under this.
    "specific_humidity": (0.0, 0.04),
    # 0 to 2000 kg/m2 (mm) - far above any real single-event
    # accumulation record (~1825 mm/24h, La Reunion 1966), generous on
    # purpose.
    "precipitation_amount": (0.0, 2000.0),
}


def check_range(value: float, standard_name: str, unit: str | None = None) -> None:
    """
    Verify `value` falls within OPERATIONAL_RANGES' documented bound
    for `standard_name`.

    Parameters
    ----------
    value : float
    standard_name : str
        A real CF standard_name with a documented range above.
    unit : str, optional
        The unit `value` is actually in, if different from the
        variable's CF canonical unit - triggers a real conversion
        (acf.normalization.units.convert_unit()) before checking, so a
        Celsius temperature is correctly checked against the Kelvin
        bound rather than compared to the wrong scale.

    Raises
    ------
    ValueError
        If `standard_name` has no documented range - add a real,
        justified bound to OPERATIONAL_RANGES rather than guessing one
        here.
    RangeError
        If `value` (after any unit conversion) falls outside the
        documented bound.
    """
    if standard_name not in OPERATIONAL_RANGES:
        raise ValueError(
            f"No documented operational range for {standard_name!r} - add one to "
            f"OPERATIONAL_RANGES with a real justification, don't guess a bound at call time"
        )

    native_unit = cf_canonical_unit(standard_name)
    if unit is not None and unit != native_unit:
        value = convert_unit(value, unit, native_unit)

    low, high = OPERATIONAL_RANGES[standard_name]
    if not (low <= value <= high):
        raise RangeError(
            f"{standard_name}={value} {native_unit} is outside ACF's documented operational "
            f"range [{low}, {high}] {native_unit} - see range_check.py's own disclosure on "
            f"what these bounds are (and are not) before treating this as a hard physical law"
        )


def check_ranges(values: dict[str, Any]) -> list[str]:
    """
    Check several (standard_name -> value) pairs at once, collecting
    every violation instead of stopping at the first.

    Parameters
    ----------
    values : dict[str, float]
        standard_name -> value, in each variable's native CF unit
        (no unit conversion here - use check_range() directly for that).

    Returns
    -------
    list[str]
        One message per out-of-range variable found; empty if none.
        Variables with no documented range are silently skipped (not
        an error here - check_ranges() is meant for opportunistic
        bulk checking of whatever a caller happens to have).
    """
    violations = []
    for standard_name, value in values.items():
        if standard_name not in OPERATIONAL_RANGES:
            continue
        try:
            check_range(value, standard_name)
        except RangeError as exc:
            violations.append(str(exc))
    return violations
