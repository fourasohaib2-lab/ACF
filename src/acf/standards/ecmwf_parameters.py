"""
ECMWF Parameter Table (GRIB Table 128 / MARS param IDs)
========================================================

Real ECMWF GRIB parameter identifiers (paramId, GRIB Table 128 - the
long-standing "operational" table used by ECMWF's MARS archive and IFS
output), for the same 9 CF standard names already scoped in
`acf.standards.grib2_tables` (see that module's docstring for the same
"correction, not fabrication" history - this file had the identical
generic auto-generated boilerplate before this pass, confirmed unused
via grep).

Scope: deliberately limited to paramIds this codebase can state with
confidence (ECMWF's own long-published Table 128, stable since before
this codebase existed) - not a full transcription of ECMWF's parameter
database (which spans several tables and thousands of derived/model-
level parameters). Extending this to other ECMWF tables (e.g. Table
228 for post-processed/derived fields) is real, disclosed future work.

Reference:
    ECMWF GRIB Table 128 (Parameter Table Version 128), as published in
    ECMWF's own parameter database (apps.ecmwf.int/codes/grib/param-db).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ECMWFParameterId:
    """A real ECMWF GRIB Table 128 parameter identifier."""

    param_id: int
    short_name: str  # ECMWF's own short name, e.g. "t", "u", "z"
    unit: str


ECMWF_PARAMETERS: dict[str, ECMWFParameterId] = {
    "air_temperature": ECMWFParameterId(130, "t", "K"),
    "specific_humidity": ECMWFParameterId(133, "q", "kg kg-1"),
    "relative_humidity": ECMWFParameterId(157, "r", "%"),
    "eastward_wind": ECMWFParameterId(131, "u", "m s-1"),
    "northward_wind": ECMWFParameterId(132, "v", "m s-1"),
    "air_pressure": ECMWFParameterId(134, "sp", "Pa"),  # surface pressure
    "air_pressure_at_mean_sea_level": ECMWFParameterId(151, "msl", "Pa"),
    "precipitation_amount": ECMWFParameterId(228, "tp", "m"),  # ECMWF reports total precip in m of water equivalent
    "surface_geopotential": ECMWFParameterId(129, "z", "m2 s-2"),
}


def get_ecmwf_parameter(cf_standard_name: str) -> ECMWFParameterId | None:
    """Real ECMWF paramId for a CF standard name, or None if not in this
    deliberately-scoped table - never a guessed/fabricated paramId."""
    return ECMWF_PARAMETERS.get(cf_standard_name)
