"""
Main normalization entry point: model-specific (name, value, unit) -> CF (standard_name, value, unit).
"""

from typing import Any

from acf.normalization.units import convert_unit
from acf.normalization.variable_names import to_cf_standard_name


def normalize_variable(
    short_name: str, value: float, source_unit: str | None = None, source: str = "ecmwf"
) -> dict[str, Any]:
    """
    Normalize one variable's (model-specific name, raw value) into the
    ACF common data model's (CF standard_name, value in the variable's
    native CF unit).

    Parameters
    ----------
    short_name : str
        Model-specific variable short name, e.g. "t2m".
    value : float
        The raw value, in `source_unit` if given, else assumed to
        already be in the reference table's native unit for this
        variable (no silent unit assumption beyond that documented
        table entry).
    source_unit : str, optional
        The unit `value` is actually in, if different from the
        reference table's native unit for this variable - triggers a
        real unit conversion (acf.normalization.units.convert_unit())
        rather than assuming `value` is already correct.
    source : str
        Which reference table `short_name` comes from (see
        variable_names.to_cf_standard_name()).

    Returns
    -------
    dict
        {
            "standard_name": ...,      # real CF standard_name
            "value": ...,               # float, in native_unit
            "unit": ...,                 # the table's native unit for this variable
            "description": ...,
        }
    """
    mapping = to_cf_standard_name(short_name, source=source)
    native_unit = mapping["unit"]

    if source_unit is not None and source_unit != native_unit:
        value = convert_unit(value, source_unit, native_unit)

    return {
        "standard_name": mapping["standard_name"],
        "value": value,
        "unit": native_unit,
        "description": mapping["description"],
    }
