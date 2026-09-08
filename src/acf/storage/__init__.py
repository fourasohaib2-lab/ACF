"""
ACF Storage Layer
====================

Part of the target architecture's API/Delivery and HPC/Compute layers
(docs/ACF_MASTER_UNIFIED_ARCHITECTURE.md - "PRODUCT ENGINE"/"storage/"
listed as a top-level package). Explicit user request "vas-y, construis
storage/", following docs/ACF_ARCHITECTURE_TARGET_GAP_MAP.md flagging
this as absent - the gap-map's own finding was precise: "pas de couche
de stockage générique (juste des writers NetCDF/Zarr ad hoc dans
data/writers/)".

What was actually found while building this (documented, not silently
fixed - see StorageWriter's own docstring): `data/writers/` contains
TWO writer classes, but both are pure-docstring stubs with zero
implementation (netcdf_writer.py, csv_writer.py - confirmed by reading
them, not assumed). The REAL, tested, wired writers already live in
`simulation_engine/output/` (NetcdfWriter, ZarrWriter - used by
forecast/engine.py, gui/esoc/command_dispatcher.py, and
tests/test_simulation_engine.py). This package does not reinvent
either: StorageWriter is a real unified facade over those two existing
real writers, plus one genuinely new real writer (CSV, via the stdlib
csv module - no pandas, which was removed from ACF's dependencies
2026-09-02 as unused).

Honest scope - what this does NOT do
---------------------------------------
GRIB2, GeoTIFF/COG and PDF export (all mentioned in the target
architecture's Product Engine layer) are NOT built here: real GRIB2
*writing* needs eccodes bindings for output (ACF's eccodes dependency
is currently only used for xarray's GRIB *read* backend - see
pyproject.toml's `formats` extra); GeoTIFF/COG need rasterio, which was
just removed from ACF's dependencies as genuinely unused. Building
either would mean re-adding a real dependency and real encoder code,
not something to fabricate a stub for.
"""

from acf.storage.writer import StorageWriter

__all__ = ["StorageWriter"]
