"""
Real unit-compatibility checking, via acf.normalization.units (MetPy/pint).
"""

from acf.core.exceptions import UnitError
from acf.normalization.units import convert_unit


def check_unit(value: float, unit: str, expected_unit: str) -> float:
    """
    Verify `unit` is dimensionally compatible with `expected_unit`, and
    return `value` converted into `expected_unit`.

    Real dimensional analysis via pint (through
    acf.normalization.units.convert_unit()) - not a lookup table of
    "known good" unit strings. A caller passing "K" where "m s-1" was
    expected gets a real UnitError, not a silent pass-through.

    Parameters
    ----------
    value : float
    unit : str
        The unit `value` is actually in.
    expected_unit : str
        The unit the caller requires.

    Returns
    -------
    float
        value converted to expected_unit.

    Raises
    ------
    UnitError
        If unit and expected_unit are not dimensionally compatible, or
        either is not a unit string pint recognizes.
    """
    try:
        return convert_unit(value, unit, expected_unit)
    except Exception as exc:
        raise UnitError(
            f"Cannot convert {value} {unit!r} to expected unit {expected_unit!r}: {exc}"
        ) from exc
