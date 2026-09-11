"""
acf.standards.wmo_tables - empty stub, no content beyond this file.

NOTE (found, corrected — post-model4d audit, 2026-09-11): previously
carried the project's generic auto-generated boilerplate ("Provides
foundational capabilities for numerical weather prediction..."), which
here was a genuine capability overclaim: this file has zero tables,
functions, or classes, and zero importers anywhere in src/ or tests/
(verified by grep). No real WMO parameter table exists anywhere in
this package today - see acf.standards.ecmwf_parameters's own
docstring for where the real ECMWF-specific parameter loading lives.
Same finding and fix applied to this file's three siblings
(ecmwf_parameters.py, grib2_tables.py, noaa_parameters.py).
"""
