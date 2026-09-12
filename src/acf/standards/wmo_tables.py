"""
WMO Code Tables (general)
=========================

NOTE (correction, 2026-09-12): this file previously contained only
generic auto-generated boilerplate ("Manage wmo tables logic and state
representations... Module functions and constants") with zero actual
tables, functions, or constants - a real docstring-overclaim (same
pattern as `grib2_tables.py`'s own correction, see that module's
docstring for the full finding). Confirmed via grep that nothing in
`src/`/`tests/` ever imported this module.

Deliberately left empty rather than populated with invented content:
unlike `grib2_tables.py` (a bounded, well-known Table 4.2 subset this
codebase could map directly from its own existing `cf_standard_names`),
"WMO code tables" as a general label spans dozens of distinct WMO
Manual on Codes tables (Common Code Table C-1 through C-14 and others)
this session did not have time to scope and verify individually without
risking a wrong/invented value - populating this honestly needs its own
dedicated pass, tracked as open work, not rushed here.

Real WMO code-table content that DOES already exist in this codebase,
elsewhere, and should be reused rather than duplicated here once this
module is scoped:
    - `acf.science.observations.wmo_code_tables` (surface/upper-air
      observation code tables)
    - `acf.standards.cf_standard_names` (CF Conventions standard names)
    - `acf.standards.grib2_tables` (GRIB2 Table 4.2 subset)

Reference:
    WMO No. 306, Manual on Codes (scope to be defined per future pass).
"""
