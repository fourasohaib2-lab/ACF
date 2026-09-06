"""
acf.data.integration - a real, self-consistent adapter-factory system
(NetCDF/GRIB/BUFR/HDF5/GeoTIFF/CSV/JSON/XML adapters, AdapterFactory,
IntegrationEngine, *_mapper.py) - but disconnected AND, separately,
each adapter's own load() is superficial.

NOTE (Physics Guard, 2026-09-06 Tier C sweep): verified by grep, not
imported anywhere in src/ - only exercised by this subpackage's own 11
dedicated test files (test_netcdf_adapter.py, test_grib_adapter.py,
etc.), not by acf.importers (the real, already-audited ingestion
system this codebase actually uses elsewhere). AdapterFactory.
get_adapter() genuinely does correct extension-based dispatch - real
logic, not fabricated. But each adapter's own load() (e.g.
NetCDFAdapter.load()) does NOT read the file's actual content (no
netCDF4/xarray open, no variable/dimension extraction) - it returns a
Dataset populated only with name/filepath/filetype metadata, empty
variables/dimensions/metadata. A caller expecting "NetCDFAdapter loads
NetCDF data" would not get that. Real, correct code for what it does
(routing + metadata), not what its name implies (actual ingestion).
"""
