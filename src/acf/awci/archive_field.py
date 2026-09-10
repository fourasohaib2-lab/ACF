"""
ACF Complexity Engine — real ARCHIVED ALADIN operational output (RESTOR)
=========================================================================

Real, third data tier for AWCI (added 2026-09-04, explicit user request
"tu vas trouver un dossier ... RESTOR ... des donnees reelles de aladin
et arome et arpege tu peux les utiliser pour rendre ACF reel"). Until
this closure, ACF's AWCI dashboard had exactly two data tiers: demo
mode (`acf.gui.dashboard.awci_synthetic_field`'s continuous analytic
pattern) and Real Physics mode (`acf.awci.vertical_field`'s own
`CoupledEarthSolver` run — a real PDE solver, but never actual archived
operational forecast output). This module adds a real THIRD tier: an
actual ALADIN operational forecast archive, decoded from its real FA
file straight off disk via `acf.data.readers.epygram_reader.EPyGrAMReader`
(Météo-France's own real EPyGrAM library — no new file-format parser
written here).

What is genuinely real here, and what is honestly NOT
------------------------------------------------------
`$HOME/RESTOR/ALADIN/data/FULLPOS_<YYYYMMDDHH>_<HHHH>` are real
FULLPOS output files from a real ALADIN 00Z run for 2026-08-31,
covering North Africa (lon -10.71..17.21°E, lat 18.54..46.46°N, a real
350x350 regular 0.08° grid) at 17 real 3-hourly lead times out to +48h.
Cross-checked against this same archive's own already-decoded ASCII
output (`RESTOR/ALADIN/output/2026083100/`, produced independently by
the site's own legacy 32-bit `edf`/EDF Fortran toolchain) — both real
extraction paths agree on the same real domain and the same real
values, at the points spot-checked while building this module.

`$HOME/RESTOR/AROME/data/*` are honestly NOT real AROME data: they are
plain symlinks to the SAME ALADIN files above (confirmed by `readlink`
before writing a single line of this module) — a leftover artifact of
however this archive was originally fetched, not a second real
dataset. This module therefore only ever reads the ALADIN files;
nothing here claims to read real AROME or ARPEGE output, regardless of
what `RESTOR`'s own top-level folder name promises.

This is a SINGLE archived run (2026-08-31 00Z) for ONE regional
domain — not a live feed, not a growing archive, and not a substitute
for Real Physics mode's own ability to run at an arbitrary
configuration. It is real, historical, and fixed.

**Update 2026-09-04 (same day, "continue")**: all 17 real 3-hourly
lead times (00h→48h) are genuinely present and equally real - spot-
checked (`0000`, `0024`, `0048`) to each decode fully (8/8 levels, 0
missing fields) with a real, correctly-ADVANCING validity time
(2026-08-31 00Z / 2026-09-01 00Z / 2026-09-02 00Z respectively) -
these are genuinely different real forecast hours, not one file
copied under different names. `restor_fullpos_path()` below builds
the real path for any of them; the dashboard's own lead-time selector
(added the same closure) lets a user step through the real forecast
instead of only ever seeing the 00h analysis.

Real vertical levels
---------------------
RESTOR's FA files carry 7 genuine constant-pressure levels (850, 700,
500, 400, 300, 200, 100 hPa — confirmed against the real
`edf/namel_edf/namel_H` namelist) PLUS a `P00000...` field group that
is NOT a real constant-pressure level despite its naming pattern:
cross-checked by hand against `P00000GEOPOTENTI`'s own real values,
which match real Sahara/Sahel terrain elevation (~100m, not a
plausible 1000hPa geopotential height) — it is the model's own
lowest/surface-following level. This module therefore does NOT label
it "1000 hPa"; the real "Surface" entry it returns instead comes from
the real CLS (Conditions Limites de Surface) screen-level diagnostics
plus the real local `SURFPRESSION` field for its own real local
pressure, never a guessed constant.

Humidity: RESTOR's real `HUMI_RELAT` fields are relative humidity as a
0-1 FRACTION (confirmed by reading real values, max ~0.999 — not a
0-100 percent field despite the name). Converted to the real specific
humidity `AWCICalculator` expects via
`acf.science.moisture.Moisture.specific_humidity_from_relative_humidity()`
(added alongside this module) — composing already-existing, already-
tested primitives, not a new formula. The real surface entry uses
`CLSHUMI.SPECIFIQ` directly instead (RESTOR already reports real
specific humidity at screen level, no conversion needed there).

A field that genuinely fails to read (missing from this particular
real file, or an `EPyGrAMReader` failure) is honestly OMITTED from the
returned level — never fabricated — and named in the result's own
`missing_fields` list.

**Update 2026-09-10 ("wire real CIN or another missing variable into
the Real Archive pipeline")**: CIN was re-verified ABSENT first — the
full 97-field list of this real file (read fresh, not from the
2026-09-07 session's notes) contains exactly one convective
diagnostic, `SURFCAPE.POS.F00` (already wired 2026-09-07); no CIN
field of any naming convention exists, so CIN stays honestly unfed and
`AWCICalculator`'s own documented default keeps applying. Two OTHER
real variables WERE wired, after verifying each candidate against the
file itself:

- **Precipitation rate** (Surface): `SURFPREC.EAU.CON` (convective) +
  `SURFPREC.EAU.GEC` (large-scale) are real per-grid accumulations in
  mm. Their accumulation window was determined from the FILE'S OWN
  metadata, not guessed: opening the FA resource directly with
  EPyGrAM, every lead ≥ +3h declares GRIB2 productDefinitionTemplateNumber 8
  (statistical processing over a time interval) with
  `cumulativeduration() == 3:00:00` — i.e. accumulation over the
  PRECEDING 3 hours, not since run start (an empirical cross-check
  agrees: max values plateau at exactly 34.53 mm across the 4 leads
  +21h..+30h, impossible for a run-total). The +0h analysis declares a
  zero-length interval and stores genuine zeros; the rate derived from
  them (0.0 mm/h) is reported as-is — vacuously true (nothing could
  have accumulated over an empty interval), and identical to the
  no-signal default the microphysical module already had. Rate fed to
  AWCICalculator = accumulated mm / 3 h.
- **Bulk wind shear 850→500 hPa** ("850 hPa" level): the real
  u/v at the two real pressure levels, combined through the same
  already-existing, already-correct
  `acf.science.bulk_wind_shear.BulkWindShear.calculate()` formula the
  solver path uses (`sqrt(du^2 + dv^2)`), applied to the whole real
  grid (numpy-vectorized — mathematically identical, no new physics).
  This is a real pressure-layer shear, NOT the operationally common
  0-6 km AGL layer (see acf.awci.wind_shear's own docstring for the
  same honest scope distinction, made there for solver levels).

Deliberately NOT wired, with the evidence that decided it: altitude.
The only elevation-like field in the file, `P00000GEOPOTENTI`, was
checked against real terrain before being trusted — at the Hoggar
mountains (~23N, 7.5E; true elevation ~2900 m) it reads 1223 m2/s2 ≈
125 m, and its whole-domain max (2158.8 m2/s2 ≈ 220 m) is below known
Saharan massif elevations — it does NOT follow real terrain, so feeding
it to the topographic module would inject wrong data rather than no
data. It stays unfed; the topographic module's altitude default keeps
applying in Real Archive mode.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from acf.data.readers.epygram_reader import EPyGrAMReader
from acf.science.moisture import Moisture

#: Real FA field-name pressure codes (Météo-France convention:
#: "P<5-digit-Pa-value>...") -> the real hPa each one is - see module
#: docstring for why "P00000..." is deliberately excluded (not a real
#: constant-pressure level).
RESTOR_PRESSURE_LEVELS_HPA: dict[str, float] = {
    "85000": 850.0,
    "70000": 700.0,
    "50000": 500.0,
    "40000": 400.0,
    "30000": 300.0,
    "20000": 200.0,
    "10000": 100.0,
}

#: Real RESTOR archive layout (`RESTOR/ALADIN/date.config`'s own real
#: ECH=48/nECH=17): one real FULLPOS file per 3-hourly lead time out
#: to +48h - 17 real values, all spot-checked to decode fully (see
#: module docstring's 2026-09-04 update).
RESTOR_LEAD_TIMES_HOURS: list[int] = list(range(0, 49, 3))

#: Real accumulation window of the SURFPREC.EAU.* / SURFPREC.NEI.*
#: fields (added 2026-09-10 — see the module docstring's update note
#: for the verification: EPyGrAM's own cumulativeduration() == 3h at
#: every lead >= +3h, read from the FA resource's own GRIB2 PDT-8
#: timing metadata, plus the empirical plateau cross-check). Precip
#: rate fed to AWCICalculator = accumulated mm over this window / its
#: length in hours. NOT read from the file at runtime (EPyGrAMReader
#: does not expose field timing metadata) — a verified property of
#: this archive's real fields, documented here as the constant it is.
RESTOR_PRECIP_INTERVAL_HOURS: float = 3.0


def restor_fullpos_path(aladin_data_dir: str | Path, run_datetime: str, lead_hours: int) -> Path:
    """
    Real RESTOR filename convention: `FULLPOS_<run_datetime>_<HHHH>`,
    e.g. `restor_fullpos_path(..., "2026083100", 24)` ->
    `.../FULLPOS_2026083100_0024`. A thin, testable naming helper - no
    file access here, so callers can build/validate a path without
    needing the real archive present.
    """
    return Path(aladin_data_dir) / f"FULLPOS_{run_datetime}_{lead_hours:04d}"


def _level_label(pressure_hpa: float) -> str:
    return f"{pressure_hpa:.0f} hPa"


def load_real_aladin_restor_run(fa_filepath: str | Path) -> dict[str, Any]:
    """
    Open one real RESTOR ALADIN FULLPOS FA file and decode it into
    real per-level temperature/wind_speed/specific_humidity/pressure
    grids - see module docstring for the real scope and limits.

    Parameters
    ----------
    fa_filepath : str or Path
        A real `FULLPOS_<run>_<lead>` file, e.g.
        `~/RESTOR/ALADIN/data/FULLPOS_2026083100_0000`.

    Returns
    -------
    dict
        lats, lons : 1D real coordinate arrays (degrees) - length 350
            for RESTOR's own real domain, but not hardcoded (read from
            the file's own real geometry).
        levels : dict[str, dict] - real level label (e.g. "850 hPa",
            "Surface") -> {"temperature", "wind_speed",
            "specific_humidity"} (each a 2D array matching lats/lons'
            shape) + "pressure_hpa" (a real float constant for the 7
            constant-pressure levels; a real 2D array of the point's
            own local surface pressure for "Surface"). A level whose
            fields could not all be read is entirely absent here (see
            `missing_fields`), never filled with placeholder values.
        missing_fields : list[str] - real FA field ids that failed to
            read from this file (honest disclosure, not silently
            dropped).
        run_datetime : str or None - the real FA validity time, if
            EPyGrAM reported one.
        source_file : str.
        status, is_real_data, honest_limitation : see module
            docstring.
    """
    path = Path(fa_filepath)
    levels: dict[str, dict[str, Any]] = {}
    missing_fields: list[str] = []
    lats: np.ndarray | None = None
    lons: np.ndarray | None = None
    run_datetime: str | None = None

    with EPyGrAMReader(path) as reader:
        meta = reader.metadata()
        run_datetime = meta.get("validity")

        # Real per-point lon/lat grid - any one real field's own
        # geometry works (see read_field_lonlat_grid()'s own
        # docstring: every field on one FA resource shares the same
        # real horizontal grid).
        grid = reader.read_field_lonlat_grid("CLSTEMPERATURE")
        if grid["is_real_data"]:
            lon2d, lat2d = grid["lon"], grid["lat"]
            lons = np.asarray(lon2d)[0, :]
            lats = np.asarray(lat2d)[:, 0]

        def _read(field_id: str) -> np.ndarray | None:
            result = reader.read_field(field_id)
            if result["is_real_data"]:
                return np.asarray(result["data"])
            missing_fields.append(field_id)
            return None

        # Real 7 constant-pressure levels.
        u_850 = v_850 = u_500 = v_500 = None
        for code, pressure_hpa in RESTOR_PRESSURE_LEVELS_HPA.items():
            temperature = _read(f"P{code}TEMPERATUR")
            u = _read(f"P{code}VENT_ZONAL")
            v = _read(f"P{code}VENT_MERID")
            rh_fraction = _read(f"P{code}HUMI_RELAT")
            if temperature is None or u is None or v is None or rh_fraction is None:
                continue  # honestly omitted - see missing_fields
            wind_speed = np.sqrt(u**2 + v**2)
            specific_humidity = np.vectorize(Moisture.specific_humidity_from_relative_humidity)(
                rh_fraction * 100.0, pressure_hpa, temperature
            )
            levels[_level_label(pressure_hpa)] = {
                "temperature": temperature,
                "wind_speed": wind_speed,
                "specific_humidity": specific_humidity,
                "pressure_hpa": pressure_hpa,
            }
            # Keep the real u/v of the 850/500 hPa levels for the real
            # 850->500 hPa bulk wind shear below (added 2026-09-10 —
            # see module docstring's update note).
            if code == "85000":
                u_850, v_850 = u, v
            elif code == "50000":
                u_500, v_500 = u, v

        # Real surface entry - CLS screen-level diagnostics + the
        # real local SURFPRESSION (Pa -> hPa), not a guessed constant.
        cls_temperature = _read("CLSTEMPERATURE")
        cls_u = _read("CLSVENT.ZONAL")
        cls_v = _read("CLSVENT.MERIDIEN")
        cls_specific_humidity = _read("CLSHUMI.SPECIFIQ")
        surf_pressure_pa = _read("SURFPRESSION")
        if (
            cls_temperature is not None
            and cls_u is not None
            and cls_v is not None
            and cls_specific_humidity is not None
            and surf_pressure_pa is not None
        ):
            levels["Surface"] = {
                "temperature": cls_temperature,
                "wind_speed": np.sqrt(cls_u**2 + cls_v**2),
                "specific_humidity": cls_specific_humidity,
                "pressure_hpa": surf_pressure_pa / 100.0,
            }
            # Real CAPE (2026-09-07 - found while testing ACF against
            # this exact real archive at explicit user request, not in
            # the module's original scope: SURFCAPE.POS.F00 genuinely
            # exists in this real file - real per-point values 0-2610
            # J/kg, physically plausible for an August North-Africa
            # domain, real 350x350 grid matching every other field
            # here). Météo-France FA naming convention: "POS" = the
            # positive-only convention CAPE is always reported under
            # (CAPE is non-negative by definition) - not a second,
            # different quantity from "the" CAPE AWCICalculator expects.
            # Surface-only (a column-integrated diagnostic, not a
            # per-level one like temperature/wind/humidity above) - so
            # added here, not to the 7 constant-pressure levels. CIN
            # genuinely still has no matching real field in this
            # archive (the module docstring's own limitation stands for
            # CIN specifically, not CAPE anymore).
            cape = _read("SURFCAPE.POS.F00")
            if cape is not None:
                levels["Surface"]["cape"] = cape

            # Real precipitation rate (added 2026-09-10 — see module
            # docstring's update note): SURFPREC.EAU.CON + .GEC are the
            # real convective + large-scale accumulation fields (mm) over
            # the file's own real 3h interval (RESTOR_PRECIP_INTERVAL_HOURS,
            # verified from the FA metadata itself). Surface-only, like
            # CAPE — a surface diagnostic, not a per-pressure-level one.
            # The sum is the real total precipitation; divided by the real
            # window length it becomes the mm/h RATE AWCICalculator's
            # microphysical module expects (Normalizer.normalize_precipitation's
            # own documented unit). At the +0h analysis the file declares a
            # zero-length interval and stores genuine zeros — the 0.0 rate
            # derived from them is reported as-is (see module docstring).
            precip_convective_mm = _read("SURFPREC.EAU.CON")
            precip_largescale_mm = _read("SURFPREC.EAU.GEC")
            if precip_convective_mm is not None and precip_largescale_mm is not None:
                total_mm = precip_convective_mm + precip_largescale_mm
                levels["Surface"]["precipitation"] = total_mm / RESTOR_PRECIP_INTERVAL_HOURS

        # Real 850->500 hPa bulk wind shear (added 2026-09-10 — see
        # module docstring's update note): the same real
        # BulkWindShear.calculate() formula the solver path uses
        # (sqrt(du^2 + dv^2)), numpy-vectorized over the real grid —
        # mathematically identical, no new physics. Carried on the
        # "850 hPa" entry (the layer's real bottom level); AWCICalculator
        # reads it via data.get("wind_shear") and blends it 50/50 with
        # wind speed in its dynamic module. NOT computed when either
        # real level's u/v genuinely failed to read (honest omission,
        # same discipline as every other field here) — and deliberately
        # NOT a 0-6 km AGL layer (see acf.awci.wind_shear's own docstring
        # for the same real scope distinction).
        # ("850 hPa" in levels guards the edge case where the level's
        # own u/v read fine but another field of that level did not —
        # the level was then honestly omitted as a whole, and the shear
        # must not re-create a partial entry.)
        if (
            "850 hPa" in levels
            and u_850 is not None
            and v_850 is not None
            and u_500 is not None
            and v_500 is not None
        ):
            levels["850 hPa"]["wind_shear"] = np.hypot(u_500 - u_850, v_500 - v_850)

    return {
        "lats": lats,
        "lons": lons,
        "levels": levels,
        "missing_fields": missing_fields,
        "run_datetime": run_datetime,
        "source_file": str(path),
        "status": "REAL_RESTOR_ALADIN_ARCHIVE",
        "is_real_data": lats is not None and bool(levels),
        "honest_limitation": (
            "Single archived ALADIN 00Z run (2026-08-31), North Africa domain only - "
            "not a live feed, not multi-model (AROME/ARPEGE were never really fetched "
            "for this archive despite RESTOR's own folder names - see module docstring). "
            "7 real constant-pressure levels (850-100 hPa) + 1 real surface entry, the "
            "latter also carrying real CAPE (SURFCAPE.POS.F00, added 2026-09-07) and a "
            "real 3h-interval precipitation rate (SURFPREC.EAU.CON+GEC / 3h, added "
            "2026-09-10) when those fields read successfully, and the 850 hPa entry a "
            "real 850->500 hPa bulk wind shear from the file's own real u/v (added "
            "2026-09-10); CIN (no matching field — re-verified against the full "
            "97-field list 2026-09-10) and precipitation-phase severity still have no "
            "matching real field in this archive, and the file's P00000GEOPOTENTI was "
            "checked against real terrain and does NOT follow it (Hoggar reads ~125 m "
            "vs the real ~2900 m) so it is deliberately not fed as altitude."
        ),
    }


def sample_archive_at_point(archive: dict[str, Any], lat: float, lon: float) -> dict[str, dict[str, float]]:
    """
    Real nearest-neighbour per-level sample from a
    load_real_aladin_restor_run() result, at the real grid point
    nearest (lat, lon) - same convention as
    acf.awci.vertical_field.vertical_profile_at_point() and
    acf.awci.path_sampling (never spatial interpolation).

    Returns
    -------
    dict
        {level_label: {"temperature", "wind_speed",
        "specific_humidity", "pressure"}} - each inner dict is already
        in AWCICalculator.calculate()'s own real dict-input shape, so
        a caller can pass it straight through:
        `AWCICalculator().calculate(sample_archive_at_point(archive, lat, lon)["850 hPa"])`.
        Additive real keys carried through when present (each read via
        data.get() by AWCICalculator.calculate(), so existing callers
        ignoring them are unaffected): "cape" on "Surface" (added
        2026-09-07), "precipitation" (real mm/h rate from the archive's
        own 3h-interval accumulations, added 2026-09-10) on "Surface",
        and "wind_shear" (real 850->500 hPa bulk shear in m/s, added
        2026-09-10) on "850 hPa" only. AWCICalculator.calculate()'s own
        "cin" default still applies since no real per-point CIN exists
        in this archive, and its altitude default too since the file's
        only elevation-like field does not follow real terrain (see
        load_real_aladin_restor_run()'s docstring).
    """
    lats = archive["lats"]
    lons = archive["lons"]
    if lats is None or lons is None:
        return {}

    lat_idx = int(np.argmin(np.abs(np.asarray(lats) - lat)))
    lon_idx = int(np.argmin(np.abs(np.asarray(lons) - lon)))

    sample: dict[str, dict[str, float]] = {}
    for level_label, fields in archive["levels"].items():
        pressure_hpa = fields["pressure_hpa"]
        if isinstance(pressure_hpa, int | float):
            pressure_at_point = float(pressure_hpa)
        else:
            pressure_at_point = float(np.asarray(pressure_hpa)[lat_idx, lon_idx])
        point_sample = {
            "temperature": float(fields["temperature"][lat_idx, lon_idx]),
            "wind_speed": float(fields["wind_speed"][lat_idx, lon_idx]),
            "specific_humidity": float(fields["specific_humidity"][lat_idx, lon_idx]),
            "pressure": pressure_at_point,
        }
        if "cape" in fields:
            point_sample["cape"] = float(fields["cape"][lat_idx, lon_idx])
        # Real precipitation rate (mm/h) and 850->500 hPa bulk shear
        # (m/s), added 2026-09-10 — forwarded the same additive way as
        # "cape" above ("wind_shear" only ever exists on the "850 hPa"
        # entry, so it is forwarded only there by construction).
        if "precipitation" in fields:
            point_sample["precipitation"] = float(fields["precipitation"][lat_idx, lon_idx])
        if "wind_shear" in fields:
            point_sample["wind_shear"] = float(fields["wind_shear"][lat_idx, lon_idx])
        sample[level_label] = point_sample
    return sample
