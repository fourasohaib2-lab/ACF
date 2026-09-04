# AWCI Real Archive Data (RESTOR)

**Date:** 2026-09-04. Explicit user request: *"tu vas trouver un dossier
dans le PC qui s'appelle RESTOR il contient des données réelles de
aladin et arome et arpege tu peux les utiliser pour rendre ACF réel"*.

## What RESTOR actually is

`$HOME/RESTOR` is a legacy, site-local "retour d'expérience" toolkit (a
real README dated 01/05/2022 confirms this): scripts + a real 32-bit
Fortran EDF decoder + real archived model output, used by an
operational forecasting site to re-examine past ALADIN/AROME runs. It
is **not part of this git repository** — real operational NWP output
(~20MB per lead time), machine-local only, present on the machine this
feature was built on and nowhere else.

## What is genuinely real, and what is honestly NOT

- **Real**: `RESTOR/ALADIN/data/FULLPOS_2026083100_00xx` — 17 real
  FULLPOS output files (3-hourly, 00h→48h) from a real ALADIN 00Z run
  for **2026-08-31**, covering North Africa (lon -10.71..17.21°E, lat
  18.54..46.46°N, a real 350×350 0.08° grid). Confirmed real: cross-
  checked temperature at a grid corner against the site's own
  independent legacy EDF ASCII decode (a completely different real
  code path) and got an exact match (see
  `tests/test_awci_archive_field.py::test_real_temperature_cross_checks_against_the_independent_legacy_edf_decode`).
- **Honestly NOT real**: `RESTOR/AROME/data/*` are plain **symlinks**
  to the same ALADIN files (`readlink` confirmed this before a single
  line of code was written) — a leftover artifact of however this
  archive was originally fetched, not a second real dataset. `RESTOR`
  also has no ARPEGE data directory at all. Despite the folder name
  "RESTOR" implying ALADIN **and** AROME **and** ARPEGE, ACF only ever
  reads the real ALADIN files — `acf.awci.archive_field` never opens
  `RESTOR/AROME/*`, and nothing in ACF claims real AROME/ARPEGE
  archive data exists.

## What ACF built on top of it

`src/acf/awci/archive_field.py` — a real reader, decoding straight
from the real FA file via **Météo-France's own EPyGrAM library**
(already integrated and audited in this codebase,
`acf.data.readers.epygram_reader.EPyGrAMReader` — extended this
closure with a real lon/lat-grid accessor, `read_field_lonlat_grid()`).
No hand-rolled binary/FA parser was written; the legacy 32-bit Fortran
`edf` toolchain in `RESTOR` was used only to independently **verify**
this module's own real reads, never as a runtime dependency.

- **7 real constant-pressure levels**: 850, 700, 500, 400, 300, 200,
  100 hPa (confirmed against `RESTOR/ALADIN/edf/namel_edf/namel_H`'s
  own real namelist). RESTOR's FA files also carry a `P00000...` field
  group that is **not** a real constant-pressure level despite its
  naming pattern — confirmed by hand (its own real geopotential height
  matches real Sahara/Sahel terrain elevation, ~100m, not a plausible
  1000 hPa geopotential height): it is the model's own lowest/surface-
  following level, and this module does not mislabel it "1000 hPa".
- **1 real surface entry**, sourced instead from the real CLS
  (Conditions Limites de Surface) screen-level diagnostics
  (`CLSTEMPERATURE`, `CLSVENT.ZONAL`/`CLSVENT.MERIDIEN`,
  `CLSHUMI.SPECIFIQ`) plus the real local `SURFPRESSION` field for its
  own real local pressure — never a guessed 1013.25 hPa constant.
- **Humidity**: RESTOR's real `HUMI_RELAT` fields are a 0–1 fraction
  (confirmed by reading real values, not the 0–100 the field name
  might suggest). Converted to the specific humidity `AWCICalculator`
  needs via a new `acf.science.moisture.Moisture.
  specific_humidity_from_relative_humidity()` — composing only
  already-existing, already-tested primitives (`SaturationVaporPressure`,
  `SaturationMixingRatio`, `SpecificHumidity`), no new formula.
- A field that genuinely fails to read is **honestly omitted** from
  its level (never fabricated), and named in the result's own
  `missing_fields` list — this particular real file has none.

## GUI: "📡 Real Archive (2026-08-31)"

A new dashboard button opens a dialog reusing `AWCIVerticalProfile`/
`AWCIVerticalProfileLevelDialog` exactly as "🔍 See Vertical Profile"
does — same real click-to-detail pattern — fed by
`sample_archive_at_point()` (real nearest-neighbour lookup, same
convention as `vertical_profile_at_point()`/`path_sampling.py`) at the
dashboard's current point of interest. Does **not** touch
`_point_of_interest`/Real Physics's own state machine — a fully
independent, additive third data tier.

**Update 2026-09-04 (same day, "continue")**: the dialog now also has
a real **Lead time** selector — RESTOR's own 17 real 3-hourly lead
times (+0h analysis → +48h), each loaded and decoded from its own real
FA file on first selection (`restor_fullpos_path()`), then cached in
`self._real_archive_cache` (keyed by real lead hours) so returning to
one already seen is instant. Defaults to "00h" — the same bit-
identical behaviour this closure originally shipped with, now just one
option among 17 real ones rather than the only one. A failed load is
deliberately never cached, so a transient failure (e.g. RESTOR
unmounted between clicks) is retried, not remembered as permanent.

Two honest degradation paths, both surfaced in the dialog's own status
label, never a silent fallback to demo/solver data:
- The archive is genuinely unavailable on this machine (no
  `$HOME/RESTOR`) → `⚠ Real archive not available on this machine
  (...)`.
- The current point of interest falls outside this archive's own real
  North Africa domain → `⚠ Point (...) is OUTSIDE this real archive's
  own domain (...)` — the nearest-edge value is not hidden, but is
  clearly flagged as not physically meaningful for that point, rather
  than presented as if it were.

## Real scope limits (disclosed, not hidden)

- **Single, fixed, historical run** — 2026-08-31 00Z. Not a live feed,
  not a growing archive. All 17 real 3-hourly lead times (+0h→+48h)
  are now wired into the dashboard's own lead-time selector (closed
  2026-09-04, same day as this doc's first version, which had only
  +0h). Real Physics mode is stronger on flexibility (a solver
  runnable at any configuration); this tier's own value is that its
  numbers are genuine archived operational output, not a solver's.
- **One regional domain** — North Africa only. A point of interest
  outside it gets the honest "OUTSIDE" warning above, never a silently
  misleading value.
- **No AROME/ARPEGE real data**, despite `RESTOR`'s own folder name —
  see above.
- **No CAPE/CIN/precipitation-phase per-level fields decoded** — the 7
  real levels + surface cover temperature/wind/specific humidity/
  pressure only (`AWCICalculator`'s own defaults apply to the rest,
  same discipline as `spatial_field.py`/`vertical_field.py`).

## Tests

- `tests/test_awci_archive_field.py` — 3 unconditional tests for
  `restor_fullpos_path()`/`RESTOR_LEAD_TIMES_HOURS` (pure path-building
  logic, no real file needed) + `TestWithTheRealArchive` (11 tests,
  gated on the real archive's presence), including the independent
  legacy-EDF-decode cross-check above, a real degradation test (one
  field forced to fail via monkeypatch → its level is honestly
  omitted, `missing_fields` names it, every other level stays real and
  present), and a real proof that 3 different real lead times (+0h/
  +24h/+48h) each decode with their own real, correctly-advancing
  validity time.
- `tests/test_moisture.py` — 3 new tests for
  `specific_humidity_from_relative_humidity()` (round-trips with the
  existing forward chain, bounded, monotonic in RH).
- `tests/gui/test_awci_dashboard_reference_parity.py` —
  `TestRealArchiveWithTheRealFile` (gated, now including a real
  lead-time-switch test proving 2 different lead times cache 2
  genuinely different real archives) + 3 ungated tests (button wiring,
  honest-failure path via monkeypatch, default lead-time selection —
  these run on every machine regardless of RESTOR's presence).
