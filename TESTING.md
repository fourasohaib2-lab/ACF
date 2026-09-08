# ACF Testing Strategy

## Test Suite Architecture
The test suite consists of 387 test modules covering over 2,160 automated tests:
- **Physics and Scientific Validation**: Exact equation checks against standard atmospheric references (WMO No. 8, Rogers & Yau, Holton, Bolton 1980).
- **Data Ingestion & Readers**: Formats parsing (NetCDF4, GRIB, BUFR, GeoTIFF, HDF5, epygram FA).
- **HPC Workflows**: Slurm/PBS job templates, stage sequencing, failure recovery, and state transitions.
- **ESOC GUI & Rendering**: Qt widgets, layer cache, map projection transformations, colormaps, and dashboards.

## Executing Tests
```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run targeted test module
pytest tests/test_thermodynamics.py

# Run with coverage report
pytest --cov=src/acf tests/
```
