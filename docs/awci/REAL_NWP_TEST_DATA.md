# Real NWP Test Data (session-local alternative to RESTOR)

**Date:** 2026-09-21. Explicit user request: *"je veux que tu ajoutes le
dossier RESTOR pour testé tout le projet acf et awci avec des vrais
données"*.

## Why RESTOR itself was not used

`$HOME/RESTOR` (see `docs/awci/AWCI_REAL_ARCHIVE_DATA.md`) is real, but
machine-local to the workstation this feature was originally built on -
not part of this git repository, not reachable from this session's
remote cloud container (confirmed: a full filesystem search found no
trace of it anywhere in this environment, and this container has no
network path to the user's personal machine). Fabricating a fake
"real" ALADIN FA/EDF file was explicitly ruled out - that would be
exactly the kind of dishonest fabrication this project's own
`AGENTS.md` and every "NOTE (correction)" in this codebase's history
argues against.

## What was used instead

This session's container has real outbound network access. Two real,
freely-licensed, publicly downloadable operational NWP sources were
used instead - the same 2 sources already named (but never actually
connected) in `acf.connectors.live_connectors.LIVE_CONNECTORS_REGISTRY`:

- **ECMWF Open Data** - a real, full-globe, 0.25° combined GRIB2 file
  for the 2026-09-21 00Z IFS run (`data/real_nwp/ecmwf_open_data/`,
  134 MB, gitignored - not committed, session-local only like RESTOR).
  Confirmed real: opens as 11 separate real cfgrib "hypercubes"
  (surface/meanSea/soilLayer/entireAtmosphere/heightAboveGround/
  isobaricInhPa/mostUnstableParcel/nominalTop level types), each with
  real, physically plausible values (`tcwv`, `t2m`, `u100`/`v100`,
  etc.). `acf.importers.readers.grib_reader.GRIBReader.read()`
  correctly refuses this file with a real, honest
  `DatasetBuildError: multiple values for unique key` rather than
  silently merging incompatible level types - a real cfgrib
  limitation on combined multi-level-type files, not a bug in this
  project's own code, and not fixed here (a real caller of a combined
  file like this one needs `filter_by_keys` per level type, same as
  any cfgrib user).
- **NOAA GFS (NOMADS filter service)** - a real, small (~330 KB),
  single-run GRIB2 subset for a Europe/North-Africa subregion
  (`data/real_nwp/noaa_gfs/gfs_<date>_00z_f000_europe_nafrica.grib2`),
  requested with `lev_2_m_above_ground`/`lev_10_m_above_ground`/
  `lev_surface`/`lev_mean_sea_level` and `TMP`/`UGRD`/`VGRD`/`PRMSL`/
  `RH` - this is the file `tests/test_grib_reader_real_data.py`'s
  gated tests actually run against. Real values confirmed: 2m
  temperature/mean-sea-level pressure/2m relative humidity all in
  physically sane ranges for the real domain and date.

Neither file is committed to git (`/data/` is already in `.gitignore`,
the same real convention RESTOR itself follows) - both are session-
local, matching this project's own established "real data lives
outside the repository" discipline. Re-download commands are in
`tests/test_grib_reader_real_data.py`'s own module docstring.

## Real bugs found and fixed by this exercise

Running the real ACF/AWCI ingestion pipeline against genuine external
data - not synthetic fixtures - surfaced 2 real, previously
undetected bugs in `acf.importers.readers` (shared by their
`acf.data.readers.*` compatibility re-exports), both now fixed with
"NOTE (correction)" disclosures in the code itself:

1. **`GRIBReader.read()` and `NetCDFReader.read()` never stored real
   variable values.** Both called `dataset.add_variable(name)` with
   only the variable's real NAME - `Dataset.add_variable()`'s own
   `value` parameter defaults to `None` - so `dataset.get_variable(x)`
   returned `None` for every real variable in every real file either
   reader ever read, silently. Coordinate arrays (latitude/longitude)
   were never registered at all. This meant
   `awci.data.model_import.compute_awci_from_imported_dataset()` (the
   real engine behind the GUI's "📂 Import Model File" button) could
   never actually compute a real AWCI score from any real imported
   file - every point extraction silently found nothing. The existing
   tests (`tests/test_netcdf_reader.py`, `tests/test_grib_reader.py`)
   never caught this because they only asserted variable NAMES were
   present, never that `get_variable()` returned real data - and
   `tests/test_grib_reader.py` in particular tests a different,
   never-opens-a-real-file compatibility class
   (`acf.data.grib_reader.GribReader`), not the one with the bug
   (`acf.importers.readers.grib_reader.GRIBReader`).
2. **`GRIBReader.read()` never recorded per-variable `units`/
   `standard_name`/`long_name` metadata** (cfgrib decodes all 3 from
   the real GRIB message - confirmed by inspection), unlike its
   sibling `NetCDFReader.read()`. Without it, `model_import`'s unit
   converter treated every matched GRIB variable's unit as absent.

Both are fixed - real decoded values, real coordinate arrays, and real
per-variable metadata are now stored by both readers - and verified
end-to-end: a real GFS GRIB2 file, read through the real, now-fixed
`GRIBReader`, correctly feeds a real `AWCICalculator` computation at a
real point (Paris, 48.85°N 2.35°E), matching real variables
(`t2m`→temperature, `prmsl`→pressure) and honestly reporting the ones
it genuinely could not find (`cape`, `wind_speed` - not requested in
this particular download) as missing, never fabricated.

## A pre-existing, unrelated environment issue (disclosed, not fixed)

Any test that imports `cfgrib` (directly or via `acf.importers.readers.
grib_reader`/`netcdf_reader`) in this specific session's container
causes a native `eccodes`/`cfgrib` C-library crash (`double free or
corruption` / `munmap_chunk(): invalid pointer`) at Python process
**exit** - confirmed to happen identically before and after this
session's code changes, and even for a test file that never opens a
real GRIB file at all. `pytest` itself reports every test correctly
("N passed") before the crash, but the process's own exit code becomes
134 (SIGABRT) instead of 0 - which a CI runner gating purely on exit
code would misreport as a failure despite every real test having
passed. This is an environment-level native-library issue (almost
certainly specific to the exact `eccodes`/`cfgrib`/`ecCodes`-native
combination installed in this particular container), not an ACF/AWCI
code defect, and is the same category of pre-existing, disclosed,
out-of-scope native crash already documented elsewhere in this
project (see the already-known native subprocess-shutdown crash in
`test_awci_app.py`, referenced earlier in this session). Not
investigated further here - out of scope for a data-ingestion fix.

## Tests

- `tests/test_netcdf_reader.py` - 2 new tests (synthetic, no network
  needed, always run): real variable/coordinate values survive a
  read, and a real synthetic-but-physically-plausible NetCDF file
  feeds a real `compute_awci_from_imported_dataset()` call end-to-end.
- `tests/test_grib_reader_real_data.py` - 5 new tests, gated on the
  real downloaded GFS file's presence (honestly SKIPPED, not faked,
  when absent - same discipline as `tests/test_awci_archive_field.py`
  for RESTOR): real file-format confirmation, real values/coordinates/
  metadata survive a read, and the full real
  read → extract → `AWCICalculator` chain, checked against
  physically-sane real value ranges (not exact equality, since the
  real data is a live download and changes run to run).
