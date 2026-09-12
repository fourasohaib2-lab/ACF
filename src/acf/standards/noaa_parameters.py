"""
NOAA/NCEP Parameter Table (GRIB1 NCEP Table 2)
================================================

Real NOAA/NCEP GRIB Edition 1 parameter numbers (NCEP Table 2 - the
classic parameter table underlying legacy NCEP products and tools such
as wgrib/degrib), for the same 9 CF standard names already scoped in
`acf.standards.grib2_tables`/`ecmwf_parameters.py` (see those modules'
docstrings for the same "correction, not fabrication" history - this
file had identical generic auto-generated boilerplate before this
pass, confirmed unused via grep).

NOTE: current NOAA/NCEP operational products (e.g. GFS) have largely
moved to WMO GRIB2 (see `acf.standards.grib2_tables` - discipline/
category/number is the same WMO Table 4.2 NOAA now uses, not a
NOAA-specific scheme). This table's real, ongoing relevance is legacy
GRIB1 data and tooling still referencing NCEP Table 2 numbers - kept
distinct rather than merged with grib2_tables.py because the numbering
scheme is genuinely different (a single flat parameter number per
GRIB1 table version, not a discipline/category/number triplet).

Scope: deliberately limited to parameter numbers this codebase can
state with confidence (NCEP Table 2's long-stable core meteorological
parameters) - not a full transcription of every NCEP table version.

Reference:
    NOAA/NCEP GRIB1 Table 2 (Parameter Table Version 2), as published in
    NCEP's own GRIB documentation.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class NOAAParameterId:
    """A real NOAA/NCEP GRIB1 Table 2 parameter number."""

    parameter_number: int
    abbreviation: str  # NCEP's own abbreviation, e.g. "TMP", "UGRD"
    unit: str


NOAA_PARAMETERS: dict[str, NOAAParameterId] = {
    "air_pressure": NOAAParameterId(1, "PRES", "Pa"),
    "surface_geopotential": NOAAParameterId(7, "HGT", "gpm"),  # geopotential height, not raw geopotential
    "air_temperature": NOAAParameterId(11, "TMP", "K"),
    "eastward_wind": NOAAParameterId(33, "UGRD", "m s-1"),
    "northward_wind": NOAAParameterId(34, "VGRD", "m s-1"),
    "specific_humidity": NOAAParameterId(51, "SPFH", "kg kg-1"),
    "relative_humidity": NOAAParameterId(52, "RH", "%"),
    "precipitation_amount": NOAAParameterId(61, "APCP", "kg m-2"),
    "air_pressure_at_mean_sea_level": NOAAParameterId(2, "PRMSL", "Pa"),
}


def get_noaa_parameter(cf_standard_name: str) -> NOAAParameterId | None:
    """Real NCEP Table 2 parameter number for a CF standard name, or
    None if not in this deliberately-scoped table - never a guessed/
    fabricated number."""
    return NOAA_PARAMETERS.get(cf_standard_name)
