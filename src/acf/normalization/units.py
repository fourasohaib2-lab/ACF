"""
Real unit conversion, via MetPy's pint-based unit registry.

Not a hand-rolled table of conversion factors - CF-style unit strings
("K", "Pa", "m s-1", "kg kg-1") are parsed directly by pint (verified:
pint understands CF's space-separated exponent notation natively), and
the actual conversion arithmetic is pint's, the same well-tested
library MetPy itself is built on and that science/parcel_ascent.py
already uses elsewhere in ACF.
"""

from metpy.units import units as mp_units

#: Standard water density used for the one CF unit pair pint cannot
#: convert by dimensional analysis alone: precipitation reported as a
#: mass per area (CF's "kg m-2") is, by universal meteorological
#: convention, numerically equal to a depth in mm of liquid water -
#: because 1 kg of water spread over 1 m2 is 1 mm deep at the standard
#: density of water, 1000 kg/m3. This is a real, uncontroversial
#: physical identity (not a guessed factor), used throughout
#: operational meteorology (e.g. "1 mm of rain" IS "1 kg/m2 of rain").
_WATER_DENSITY_KG_PER_M3 = 1000.0


def convert_unit(value: float, from_unit: str, to_unit: str) -> float:
    """
    Convert `value` from `from_unit` to `to_unit` via MetPy/pint.

    Parameters
    ----------
    value : float
    from_unit, to_unit : str
        Unit strings pint understands. CF-style strings (space-
        separated exponents, e.g. "m s-1", "kg kg-1", "kg m-2") work
        directly - verified against pint's real parser, not assumed.

    Returns
    -------
    float
        value converted to to_unit.

    Raises
    ------
    Exception
        Pint's own error (e.g. `pint.errors.DimensionalityError`) if
        from_unit and to_unit are not dimensionally compatible -
        propagated, not silently caught. A genuine unit mismatch (e.g.
        converting Kelvin to knots) must fail loudly, not return a
        meaningless number. Precipitation's kg m-2 <-> mm case is the
        one dimensionally "incompatible" pair this module handles on
        purpose - see convert_precipitation_kg_m2_to_mm() /
        convert_precipitation_mm_to_kg_m2() below.
    """
    quantity = value * mp_units(from_unit)
    return float(quantity.to(to_unit).magnitude)


def convert_precipitation_kg_m2_to_mm(value_kg_m2: float) -> float:
    """
    Real conversion: kg/m2 of precipitation -> mm of liquid water depth.

    Derivation (not a magic 1:1 shortcut): depth_m = mass_per_area /
    density = value_kg_m2 / 1000.0 kg/m3, then depth_mm = depth_m *
    1000.0 (m -> mm). Because water's density is exactly 1000 kg/m3,
    these two factors of 1000 cancel - 1 kg/m2 of water IS exactly 1 mm
    deep, a real, well-known meteorological identity, not a
    coincidence of this implementation. Kept as an explicit two-step
    computation (not collapsed to `return value_kg_m2`) so the
    derivation stays visible and auditable.
    """
    depth_m = value_kg_m2 / _WATER_DENSITY_KG_PER_M3
    return depth_m * 1000.0


def convert_precipitation_mm_to_kg_m2(value_mm: float) -> float:
    """Real conversion: mm of liquid water depth -> kg/m2 of precipitation. See convert_precipitation_kg_m2_to_mm()'s own docstring for the derivation."""
    depth_m = value_mm / 1000.0
    return depth_m * _WATER_DENSITY_KG_PER_M3
