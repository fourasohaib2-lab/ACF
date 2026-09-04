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
            "7 real constant-pressure levels (850-100 hPa) + 1 real surface entry; no "
            "CAPE/CIN/precipitation-phase per-level fields decoded here."
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
        sample[level_label] = {
            "temperature": float(fields["temperature"][lat_idx, lon_idx]),
            "wind_speed": float(fields["wind_speed"][lat_idx, lon_idx]),
            "specific_humidity": float(fields["specific_humidity"][lat_idx, lon_idx]),
            "pressure": pressure_at_point,
        }
    return sample
