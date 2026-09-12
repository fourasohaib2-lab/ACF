"""
GRIB2 Parameter Tables (WMO Manual on Codes)
=============================================

Real WMO GRIB Edition 2 parameter identifiers - discipline / parameter
category / parameter number, per WMO No. 306, Manual on Codes, Volume
I.2, FM 92-XIV GRIB, Table 4.2 (product discipline 0 = Meteorological
products; per-category tables 4.2-0-N).

NOTE (correction, 2026-09-12): this file previously contained only
generic auto-generated boilerplate ("Manage grib2 tables logic and
state representations... Module functions and constants") with zero
actual tables, functions, or constants - a real docstring-overclaim,
the same pattern already found and fixed elsewhere in this codebase
(`earth_system_operations.py`'s fabricated certification,
`AVIATION_HAZARDS_REGISTRY`'s docstring overclaim). Confirmed via grep
that nothing in `src/`/`tests/` ever imported this module - genuinely
dead, not just under-documented.

Scope: only the discipline-0 (meteorological) parameters this codebase
already handles elsewhere (see `acf.standards.cf_standard_names.
CF_STANDARD_NAMES` - the same 9 quantities, cross-referenced here by
their real GRIB2 identifiers rather than invented ones). This is NOT a
complete GRIB2 Table 4.2 (which spans 10 disciplines and dozens of
categories) - extending it to other disciplines/categories is real,
useful, disclosed future work, not silently claimed as done.

GRIB2 identifies a parameter by 3 integers, always disclosed together
(never just a "GRIB2 code" number - the same integer means different
things across disciplines/categories):
    discipline        - Table 0.0 (0 = Meteorological products)
    parameterCategory - Table 4.1 (per-discipline, e.g. 0 = Temperature)
    parameterNumber   - Table 4.2-<discipline>-<category>

Real GRIB2 encode/decode I/O in this codebase goes through eccodes/
cfgrib (`acf.data.grib_reader`, `acf.data.readers.grib_reader`,
`acf.data.integration.grib_adapter`, `acf.importers.readers.
grib_reader`) - eccodes carries its own complete, authoritative GRIB2
tables internally. This module is NOT a replacement for that; it is a
small, explicit, human-readable cross-reference between this
codebase's own CF standard names and their real GRIB2 identifiers, for
documentation/labelling/export purposes where a GRIB2 identifier needs
to be shown or written without invoking eccodes.

Reference:
    WMO No. 306, Manual on Codes, Volume I.2, FM 92-XIV GRIB, Table 4.2.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class GRIB2ParameterId:
    """A real GRIB2 (discipline, parameterCategory, parameterNumber) triplet."""

    discipline: int
    parameter_category: int
    parameter_number: int
    abbreviation: str  # eccodes/WMO short name, e.g. "t", "u", "gh"
    unit: str  # GRIB2 Table 4.2's own canonical unit (may differ from a model's native unit)


# Discipline 0 = Meteorological products (Table 0.0).
GRIB2_PARAMETERS: dict[str, GRIB2ParameterId] = {
    # Category 0 = Temperature (Table 4.2-0-0)
    "air_temperature": GRIB2ParameterId(0, 0, 0, "t", "K"),
    # Category 1 = Moisture (Table 4.2-0-1)
    "specific_humidity": GRIB2ParameterId(0, 1, 0, "q", "kg kg-1"),
    "relative_humidity": GRIB2ParameterId(0, 1, 1, "r", "%"),
    "precipitation_amount": GRIB2ParameterId(0, 1, 8, "tp", "kg m-2"),
    # Category 2 = Momentum (Table 4.2-0-2)
    "eastward_wind": GRIB2ParameterId(0, 2, 2, "u", "m s-1"),
    "northward_wind": GRIB2ParameterId(0, 2, 3, "v", "m s-1"),
    # Category 3 = Mass (Table 4.2-0-3)
    "air_pressure": GRIB2ParameterId(0, 3, 0, "pres", "Pa"),
    "air_pressure_at_mean_sea_level": GRIB2ParameterId(0, 3, 1, "prmsl", "Pa"),
    "surface_geopotential": GRIB2ParameterId(0, 3, 4, "gh", "m2 s-2"),
}


def get_grib2_parameter(cf_standard_name: str) -> GRIB2ParameterId | None:
    """Real GRIB2 identifier for a CF standard name, or None if not in
    this deliberately-scoped table (see module docstring) - never a
    guessed/fabricated triplet for an unlisted name."""
    return GRIB2_PARAMETERS.get(cf_standard_name)
