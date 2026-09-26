"""
NOAA GFS 0.25° as a second model for AWCI (spec SP6 §2-3): download by HTTP byte ranges from NOAA Open Data
Dissemination (public domain), decode, and hand the unchanged pipeline (compute_step) the IFS field names and units.

Source: https://noaa-gfs-bdp-pds.s3.amazonaws.com/gfs.{YYYYMMDD}/{HH}/atmos/gfs.t{HH}z.pgrb2.0p25.f{FFF}, with its
.idx (wgrib2 inventory: "n:offset:d=YYYYMMDDHH:VAR:level:time:"); a message spans from its offset to the next one.

Field correspondence (IFS <- GFS), differences stated, never hidden (they are listed in each cube's manifest):
- t, q, u, v, w (Pa/s), gh (gpm) <- TMP, SPFH, UGRD, VGRD, VVEL, HGT on the same 12 pressure levels;
- r <- recomputed from q, T, p with the IFS mixed-phase saturation (acf.awci.ops.thermo.ifs_relative_humidity_pct);
- d <- horizontal divergence of (u, v) on the sphere (acf.awci.ops.kinematics.horizontal_divergence);
- 2t, 2d, 10u, 10v, sp, msl <- TMP/DPT 2 m, UGRD/VGRD 10 m, PRES surface, PRMSL;
- 10fg <- GUST surface: instantaneous gust, where the IFS gives the maximum since the previous post-processing;
- mucape <- CAPE 255-0 hPa above ground (most unstable parcel in the lowest 255 hPa; IFS: lowest 350 hPa);
- tprate <- PRATE (instantaneous, kg m-2 s-1);
- ptype <- CRAIN, CSNOW, CFRZR, CICEP (0/1) as ECMWF codes by severity: freezing rain 3 > ice pellets 8 >
  rain and snow together 7 (mixed) > snow 5 > rain 1; none 0;
- tcc <- TCDC entire atmosphere / 100; lsm <- LAND (0/1, not a fraction);
- tcwv <- PWAT; tcw <- PWAT + CWAT: CWAT is cloud water only, so the column condensate excludes rain and snow;
- ttr <- ULWRF at the top of the atmosphere, averaged over 6-hour buckets (f003: 0-3 h, f006: 0-6 h, f009: 6-9 h…):
  the IFS accumulation is rebuilt, ttr(t) = ttr(b) - mean(b, t) x (t - b) x 3600 s, b = start of the bucket
  (incoming longwave at the top of the atmosphere is nil, so net = -upward); needs the bucket start, else NaN;
- tp <- APCP "0-N hour acc" (mm) / 1000; ttr = tp = 0 at step 0 (accumulations since the analysis);
- sd, rsn <- WEASD / 1000 (m water equivalent) and WEASD / SNOD (kg m-3) where SNOD > 0;
- sf (snowfall) has no GFS counterpart in pgrb2.0p25: NaN, so the GFS cube has no snowfall layer.
"""

from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime

import numpy as np

from acf.awci.ops.decode import StepFields, _read
from acf.awci.ops.domains import Domain
from acf.awci.ops.kinematics import horizontal_divergence
from acf.awci.ops.source_ecmwf import PL_LEVELS, Fetcher, MissingFieldsError
from acf.awci.ops.thermo import ifs_relative_humidity_pct

BASE_URL = "https://noaa-gfs-bdp-pds.s3.amazonaws.com"
MODEL = "NOAA GFS 0.25° (NOAA Open Data Dissemination)"
LICENSE = "public domain (NOAA)"
ATTRIBUTION = "NOAA/NCEP GFS, domaine public"
BUCKET_H = 6  # GFS averages and bucket accumulations restart every 6 hours
PL_VARS = {"t": "TMP", "q": "SPFH", "u": "UGRD", "v": "VGRD", "w": "VVEL", "gh": "HGT"}
SFC_VARS: dict[str, tuple[str, str]] = {
    "2t": ("TMP", "2 m above ground"), "2d": ("DPT", "2 m above ground"), "10u": ("UGRD", "10 m above ground"),
    "10v": ("VGRD", "10 m above ground"), "gust": ("GUST", "surface"), "sp": ("PRES", "surface"),
    "msl": ("PRMSL", "mean sea level"), "mucape": ("CAPE", "255-0 mb above ground"), "prate": ("PRATE", "surface"),
    "crain": ("CRAIN", "surface"), "csnow": ("CSNOW", "surface"), "cfrzr": ("CFRZR", "surface"),
    "cicep": ("CICEP", "surface"), "tcc": ("TCDC", "entire atmosphere"), "land": ("LAND", "surface"),
    "pwat": ("PWAT", "entire atmosphere (considered as a single layer)"),
    "cwat": ("CWAT", "entire atmosphere (considered as a single layer)"),
    "weasd": ("WEASD", "surface"), "snod": ("SNOD", "surface"),
}
#: Definition differences written to each GFS cube manifest (spec SP6 §3).
DIFFERENCES = {
    "r": "recomputed from q, T, p with the IFS mixed-phase saturation",
    "d": "horizontal divergence of (u, v), centred differences on the sphere",
    "10fg": "GFS GUST is instantaneous (IFS: maximum since the previous post-processing)",
    "mucape": "GFS CAPE 255-0 hPa above ground (IFS: most unstable parcel in the lowest 350 hPa)",
    "ptype": "from the GFS categorical types CRAIN, CSNOW, CFRZR, CICEP",
    "lsm": "GFS LAND mask (0/1), not a fraction",
    "tcw": "PWAT + CWAT: cloud water only, rain and snow excluded",
    "ttr": "rebuilt from 6-hour bucket averages of top-of-atmosphere upward longwave",
    "sf": "no GFS counterpart: no snowfall layer",
}
_LINE = re.compile(r"^\d+:(\d+):d=\d{10}:([^:]+):([^:]+):([^:]+):")


@dataclass(frozen=True)
class GfsEntry:
    var: str
    level: str
    time: str
    offset: int
    length: int | None  # None for the last message of the file (unknown end)


def gfs_step_urls(run: datetime, step: int) -> tuple[str, str]:
    stem = f"{BASE_URL}/gfs.{run:%Y%m%d}/{run:%H}/atmos/gfs.t{run:%H}z.pgrb2.0p25.f{step:03d}"
    return stem, f"{stem}.idx"


def parse_gfs_index(text: str) -> list[GfsEntry]:
    parsed = [m.groups() for m in map(_LINE.match, text.splitlines()) if m]
    offsets = [int(p[0]) for p in parsed]
    return [GfsEntry(var, level, time, off, (offsets[i + 1] - off) if i + 1 < len(offsets) else None)
            for i, ((_, var, level, time), off) in enumerate(zip(parsed, offsets))]


def _instant(step: int) -> str:
    return "anl" if step == 0 else f"{step} hour fcst"


def bucket_start(step: int) -> int:
    return ((step - 1) // BUCKET_H) * BUCKET_H


def wanted_keys(step: int) -> dict[str, tuple[str, str, str]]:
    """key -> (var, level, time) of every message needed at this step."""
    t = _instant(step)
    keys = {f"{k}@{p}": (var, f"{p} mb", t) for k, var in PL_VARS.items() for p in PL_LEVELS}
    keys |= {k: (var, level, t) for k, (var, level) in SFC_VARS.items()}
    if step > 0:
        keys["apcp"] = ("APCP", "surface", f"0-{step} hour acc fcst")
        keys["ulwrf_toa"] = ("ULWRF", "top of atmosphere", f"{bucket_start(step)}-{step} hour ave fcst")
    return keys


def select_gfs_entries(entries: list[GfsEntry], step: int) -> dict[str, GfsEntry]:
    by_id: dict[tuple[str, str, str], GfsEntry] = {}
    for e in entries:
        by_id.setdefault((e.var, e.level, e.time), e)  # APCP 0-N acc may appear twice at f003/f006: same field
    wanted = wanted_keys(step)
    missing = [k for k, ident in wanted.items() if ident not in by_id or by_id[ident].length is None]
    if missing:
        raise MissingFieldsError(f"GFS index lacks {missing}")
    return {k: by_id[ident] for k, ident in wanted.items()}


def fetch_gfs_step(fetcher: Fetcher, run: datetime, step: int, max_workers: int = 8) -> dict[str, bytes]:
    grib_url, index_url = gfs_step_urls(run, step)
    chosen = select_gfs_entries(parse_gfs_index(fetcher.get_text(index_url)), step)
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        data = list(pool.map(lambda e: fetcher.get_range(grib_url, e.offset, e.length or 0), chosen.values()))
    return dict(zip(chosen.keys(), data))


def ptype_codes(crain: np.ndarray, csnow: np.ndarray, cfrzr: np.ndarray, cicep: np.ndarray) -> np.ndarray:
    """ECMWF precipitation-type codes from the GFS categorical flags (module doc), NaN where a flag is missing."""
    flags = [np.asarray(a, dtype=float) for a in (crain, csnow, cfrzr, cicep)]
    rain, snow, frz, pel = (f >= 0.5 for f in flags)
    out = np.select([frz, pel, rain & snow, snow, rain], [3.0, 8.0, 7.0, 5.0, 1.0], default=0.0)
    return np.where(np.all([np.isfinite(f) for f in flags], axis=0), out, np.nan)


@dataclass
class GfsRunState:
    """Per-run, per-domain top-of-atmosphere accumulation at the last bucket boundary (ttr rebuild)."""

    ttr_at: dict[tuple[str, int], np.ndarray] = field(default_factory=dict)

    def ttr(self, domain: str, step: int, mean_w_m2: np.ndarray | None) -> np.ndarray | None:
        if step == 0:
            return None
        b = bucket_start(step)
        base = np.zeros_like(mean_w_m2) if b == 0 else self.ttr_at.get((domain, b))
        if base is None or mean_w_m2 is None:
            return None
        acc = base - np.asarray(mean_w_m2, dtype=float) * (step - b) * 3600.0
        if step % BUCKET_H == 0:
            self.ttr_at[(domain, step)] = acc
        return acc


def decode_gfs(messages: dict[str, bytes], domains: list[Domain], step: int, state: GfsRunState) -> dict[str, StepFields]:
    decoded: dict[str, np.ndarray] = {}
    lats = lons = None
    for key, message in messages.items():
        _, _, m_lats, m_lons, values = _read(message)
        lat_order, lon_order = np.argsort(m_lats), np.argsort(m_lons)
        if lats is None:
            lats, lons = m_lats[lat_order], m_lons[lon_order]
        decoded[key] = values[np.ix_(lat_order, lon_order)]
    if lats is None or lons is None:
        raise ValueError("no GFS message decoded")
    out: dict[str, StepFields] = {}
    levels = np.asarray(PL_LEVELS, dtype=float)
    for domain in domains:
        iy, ix = domain.crop_indices(lats, lons)
        sub = lambda key: decoded[key][np.ix_(iy, ix)]  # noqa: E731
        d_lats, d_lons = lats[iy], lons[ix]
        pl = {k: np.stack([sub(f"{k}@{p}") for p in PL_LEVELS]) for k in PL_VARS}
        p3d = levels[:, None, None] * np.ones_like(pl["t"])
        pl["r"] = ifs_relative_humidity_pct(pl["t"], pl["q"], p3d)
        pl["d"] = horizontal_divergence(pl["u"], pl["v"], d_lats, d_lons)
        s = {k: sub(k) for k in SFC_VARS}
        shape = s["sp"].shape
        weasd, snod = s["weasd"], s["snod"]
        ttr = state.ttr(domain.name, step, sub("ulwrf_toa") if step > 0 else None)
        with np.errstate(divide="ignore", invalid="ignore"):
            rsn = np.where(snod > 0, weasd / snod, np.nan)
        out[domain.name] = StepFields(lats=d_lats, lons=d_lons, levels_hpa=levels, pl=pl, sfc={
            "2t": s["2t"], "2d": s["2d"], "10u": s["10u"], "10v": s["10v"], "10fg": s["gust"], "sp": s["sp"],
            "msl": s["msl"], "mucape": s["mucape"], "tprate": s["prate"],
            "ptype": ptype_codes(s["crain"], s["csnow"], s["cfrzr"], s["cicep"]), "tcc": s["tcc"] / 100.0,
            "lsm": s["land"], "tcw": s["pwat"] + s["cwat"], "tcwv": s["pwat"],
            "ttr": np.zeros(shape) if step == 0 else (ttr if ttr is not None else np.full(shape, np.nan)),
            "sf": np.full(shape, np.nan), "sd": weasd / 1000.0, "rsn": rsn,
            "tp": np.zeros(shape) if step == 0 else sub("apcp") / 1000.0,
        })
    return out
