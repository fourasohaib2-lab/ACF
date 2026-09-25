"""
One forecast step: decoded IFS fields -> every served layer + operational AWCI.

Pressure levels below the model surface (level pressure > surface pressure sp) are
extrapolated by IFS, not real atmosphere: every per-level layer is NaN there.
Icing uses relative humidity over water computed from q, T, p (IFS `r` is relative to
ice below -23 degC and mixed-phase between -23 and 0 degC).
Clouds (SP1C) use IFS `r` as is: its mixed-phase saturation is the one of the IFS cloud scheme.
Accumulated fields (ttr, sf, tp) need the previous ingested step; without it they are NaN.
Heights above ground use the surface height: SRTM15+ over land (lsm >= 0.5), 0 m over sea
(SRTM15+ carries bathymetry, which must never lift cloud bases or ceilings).
"""

from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

import numpy as np

from acf.awci.ops.accum import accumulated_layers, column_condensate, snow_depth_cm
from acf.awci.ops.cloud_profile import CloudProfile, load_cloud_profile
from acf.awci.ops.clouds import CloudInputs, diagnose_clouds
from acf.awci.ops.engine import Profile, combine, level_codes, operational_module_scores
from acf.awci.ops.hazards import (
    dust_proxy,
    icing_potential,
    precip_class_codes,
    precip_rate_mm_h,
    ptype_severity,
    relative_humidity_2m_pct,
)
from acf.awci.ops.kinematics import cat_category_codes, ellrod_ti2, layer_shear, wind_speed
from acf.awci.ops.parcel import surface_parcel
from acf.awci.ops.registry import LEVEL_LAYERS, MODULES, SURFACE_LAYERS
from acf.awci.ops.thermo import cloud_base_lcl_m, relative_humidity_pct, theta_e_bolton_k

if TYPE_CHECKING:
    from acf.awci.ops.decode import StepFields

__all__ = ["LEVEL_LAYERS", "SURFACE_LAYERS", "compute_step"]


LAND_FRACTION_THRESHOLD = 0.5  # ECMWF convention: a grid point is land when lsm >= 0.5


def surface_height_m(elevation: np.ndarray, lsm: np.ndarray) -> np.ndarray:
    """Terrain height over land, sea level (0 m) over sea; land below sea level keeps its real height."""
    return np.where(np.asarray(lsm, dtype=float) >= LAND_FRACTION_THRESHOLD, elevation, 0.0)


@lru_cache(maxsize=1)
def _default_cloud_profile() -> CloudProfile:
    return load_cloud_profile()


def compute_step(
    fields: "StepFields", elevation: np.ndarray, profile: Profile, cloud_profile: CloudProfile | None = None,
    previous: "StepFields | None" = None, interval_h: float | None = None,
) -> dict[str, np.ndarray]:
    pl, sfc = fields.pl, fields.sfc
    cloud_profile = cloud_profile or _default_cloud_profile()
    elevation = np.asarray(elevation, dtype=float)
    underground = fields.levels_hpa[:, None, None] > (sfc["sp"] / 100.0)[None]
    p3d = fields.levels_hpa[:, None, None] * np.ones_like(pl["t"])
    ws = wind_speed(pl["u"], pl["v"])
    shear, vws = layer_shear(pl["u"], pl["v"], pl["gh"])
    ti2 = ellrod_ti2(pl["u"], pl["v"], pl["gh"], pl["d"], fields.lats, fields.lons)
    theta_e = theta_e_bolton_k(pl["t"], pl["q"], p3d)
    rate = precip_rate_mm_h(sfc["tprate"])
    severity = ptype_severity(sfc["ptype"])
    rh2m = relative_humidity_2m_pct(sfc["2t"], sfc["2d"])

    scores = operational_module_scores(
        wind_speed=ws, layer_shear=shear, theta_e=theta_e, mucape=sfc["mucape"][None],
        precip_rate=rate[None], ptype_severity=severity[None], elevation=elevation[None],
    )
    composite = combine(scores, profile)
    shape = pl["t"].shape
    layers: dict[str, np.ndarray] = {p: pl[p] for p in ("t", "q", "r", "u", "v", "w", "gh")}
    layers.update(
        wind_speed=ws, layer_shear=shear, vertical_shear=vws, cat_ti2=ti2,
        cat_category=cat_category_codes(ti2).astype(float), icing_potential=icing_potential(pl["t"], relative_humidity_pct(pl["t"], pl["q"], p3d)),
        theta_e=theta_e, awci=composite.awci, awci_level=level_codes(composite.awci, profile).astype(float),
    )
    for module in MODULES:
        layers[f"module_{module}"] = np.broadcast_to(np.asarray(scores[module], dtype=float), shape).copy()
    surface = surface_height_m(elevation, sfc["lsm"])
    lcl = cloud_base_lcl_m(sfc["2t"], sfc["2d"])
    condensate = column_condensate(sfc["tcw"], sfc["tcwv"])
    parcel = surface_parcel(sfc["2t"], sfc["2d"], sfc["sp"] / 100.0, fields.levels_hpa, pl["t"], pl["q"], pl["gh"],
                            underground)
    clouds = diagnose_clouds(CloudInputs(
        levels_hpa=fields.levels_hpa, lats=fields.lats, lons=fields.lons, r_pct=pl["r"], t_k=pl["t"], q=pl["q"],
        gh=pl["gh"], u=pl["u"], v=pl["v"], theta_e=theta_e, underground=underground, sp_hpa=sfc["sp"] / 100.0,
        elevation=surface, precip_rate_mm_h=rate, ptype=sfc["ptype"], wind10_m_s=wind_speed(sfc["10u"], sfc["10v"]),
        mucape=sfc["mucape"], column_condensate=condensate, lcl_agl_m=lcl, parcel=parcel,
    ), cloud_profile)
    layers.update(clouds)
    layers.update(accumulated_layers(sfc, previous.sfc if previous is not None else None, interval_h))
    layers.update(
        surface_height_m=surface, column_condensate=condensate, snow_depth_cm=snow_depth_cm(sfc["sd"], sfc["rsn"]),
        cloud_cover_bias=clouds["cloud_cover_total_diag"] - sfc["tcc"],
    )
    layers.update(
        t2m=sfc["2t"], d2m=sfc["2d"], rh2m=rh2m, mucape=sfc["mucape"],
        cloud_base_lcl=lcl, precip_rate=rate,
        precip_class=precip_class_codes(rate).astype(float), precip_type=sfc["ptype"], ptype_severity=severity,
        gust_10m=sfc["10fg"], dust_proxy=dust_proxy(sfc["10fg"], rh2m), tcc=sfc["tcc"], sp_hpa=sfc["sp"] / 100.0,
    )
    for name in LEVEL_LAYERS:
        layers[name] = np.where(underground, np.nan, layers[name])
    for name in ("cat_category", "awci_level", "precip_class"):
        layers[name] = np.where(layers[name] < 0, np.nan, layers[name])
    return layers
