"""
acf.io.readers - empty stub, not implemented.

Verified 2026-09-06: this subpackage has no content beyond this file and
no importer anywhere in src/ or tests/. Real reader implementations
(NetCDF4, GRIB, HDF5, GeoTIFF, BUFR, epygram FA/LFI) live in
`acf.importers`, which the rest of `acf.io` (`__init__.py`, `factory.py`,
`base_reader.py`, `manager.py`, `registry.py`) re-exports as a
compatibility layer - see those files for the real, tested API
(tests/test_io_framework.py, tests/test_importers_consolidation.py,
tests/test_compatibility_reexports.py).
"""
