"""
Model-specific variable name -> CF standard_name mapping.

Loads the real JSON reference tables under
src/acf/resources/standards/ - resources/standards/ecmwf/
parameters.json (model short name -> CF standard_name + native unit)
and resources/standards/cf/cf_standard_names.json (CF standard_name ->
its canonical CF unit). Both tables already existed in this repo,
correct and real, but were never loaded by any code before this
package (confirmed: grep for "parameters.json"/"cf_standard_names.json"
across all of src/ found zero readers) - wired in here rather than
duplicated.

Honest scope: coverage is exactly what these two JSON files contain
today - a handful of common surface variables (2m temperature, 10m
wind components, mean sea level pressure). This is not a
comprehensive WMO/GRIB2/ECMWF parameter table; extending coverage
means adding real, checked entries to the JSON files themselves, not
guessing new ones here.
"""

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

_RESOURCES_DIR = Path(__file__).resolve().parent.parent / "resources" / "standards"
_ECMWF_PARAMETERS_PATH = _RESOURCES_DIR / "ecmwf" / "parameters.json"
_CF_STANDARD_NAMES_PATH = _RESOURCES_DIR / "cf" / "cf_standard_names.json"


@lru_cache(maxsize=1)
def _load_ecmwf_parameters() -> dict[str, Any]:
    with open(_ECMWF_PARAMETERS_PATH, encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def _load_cf_standard_names() -> dict[str, Any]:
    with open(_CF_STANDARD_NAMES_PATH, encoding="utf-8") as f:
        return json.load(f)


def to_cf_standard_name(short_name: str, source: str = "ecmwf") -> dict[str, str]:
    """
    Map a model-specific variable short name to its real CF
    standard_name and native unit, from the actual reference table.

    Parameters
    ----------
    short_name : str
        Model-specific variable name, e.g. "t2m" (ECMWF's 2m
        temperature short name).
    source : str
        Which reference table to use. Only "ecmwf" is backed by a
        real table today (resources/standards/ecmwf/parameters.json) -
        any other value raises ValueError rather than silently
        returning a guessed mapping.

    Returns
    -------
    dict
        {"standard_name": ..., "unit": ..., "description": ...} - the
        table's own real entry, not invented.

    Raises
    ------
    ValueError
        If `source` has no backing table, or `short_name` is not in
        that table (honest "not found", not a fabricated guess).
    """
    if source != "ecmwf":
        raise ValueError(f"No real reference table for source={source!r} - only 'ecmwf' is backed by real data today")

    table = _load_ecmwf_parameters()
    if short_name not in table:
        raise ValueError(
            f"{short_name!r} is not in resources/standards/ecmwf/parameters.json's real table "
            f"(known: {sorted(table)}) - add a real, checked entry there to extend coverage"
        )

    entry = table[short_name]
    return {
        "standard_name": entry["standard_name"],
        "unit": entry["unit"],
        "description": entry["name"],
    }


def cf_canonical_unit(standard_name: str) -> str:
    """
    Return a CF standard_name's real canonical unit, from
    resources/standards/cf/cf_standard_names.json.

    Raises
    ------
    ValueError
        If `standard_name` is not in the real table.
    """
    table = _load_cf_standard_names()
    if standard_name not in table:
        raise ValueError(
            f"{standard_name!r} is not in resources/standards/cf/cf_standard_names.json's "
            f"real table (known: {sorted(table)})"
        )
    return str(table[standard_name]["units"])
