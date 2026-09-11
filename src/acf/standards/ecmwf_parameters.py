"""
acf.standards.ecmwf_parameters - empty stub, no content beyond this file.

NOTE (found, corrected — post-model4d audit, 2026-09-11): previously
carried the project's generic auto-generated boilerplate ("Provides
foundational capabilities for numerical weather prediction..."), which
here was a genuine capability overclaim: this file has zero tables,
functions, or classes, and zero importers anywhere in src/ or tests/
(verified by grep). The real ECMWF parameter loading this package's own docstring refers
to is `acf.standards.ecmwf.manager.ECMWFManager`/`acf.standards.hub.
StandardsHub.load_ecmwf()` (genuinely reads resources/standards/ecmwf/
parameters.json via acf.importers.ecmwf.importer.ECMWFImporter, real
and tested - see tests/test_ecmwf_manager.py, tests/
test_standards_hub.py, and acf.catalogs.ecmwf.catalog for a real
caller). This module (ecmwf_parameters.py) itself has no relation to
that real path. Same finding and fix applied to this file's three
siblings (grib2_tables.py, noaa_parameters.py, wmo_tables.py); see
acf.standards.ecmwf.catalog's own docstring for a related but distinct
finding (a disconnected empty ECMWF_PARAMETERS dict in that module).
"""
