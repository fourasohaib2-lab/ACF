"""One forecast step: decoded IFS fields -> every served layer + operational AWCI."""

from __future__ import annotations

import numpy as np

from acf.awci.ops.decode import StepFields
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
from acf.awci.ops.thermo import cloud_base_lcl_m, theta_e_bolton_k

_MODULES = ("dynamic", "thermodynamic", "convective", "microphysical", "topographic")
LEVEL_LAYERS: tuple[str, ...] = (
    "t", "q", "r", "u", "v", "w", "gh", "wind_speed", "layer_shear", "vertical_shear", "cat_ti2",
    "cat_category", "icing_potential", "theta_e", "awci", "awci_level", *(f"module_{m}" for m in _MODULES),
)
SURFACE_LAYERS: tuple[str, ...] = (
    "t2m", "d2m", "rh2m", "mucape", "cloud_base_lcl", "precip_rate", "precip_class", "precip_type",
    "ptype_severity", "gust_10m", "dust_proxy", "tcc", "sp_hpa",
)


def compute_step(fields: StepFields, elevation: np.ndarray, profile: Profile) -> dict[str, np.ndarray]:
    pl, sfc = fields.pl, fields.sfc
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
        precip_rate=rate[None], ptype_severity=severity[None], elevation=np.asarray(elevation, dtype=float)[None],
    )
    composite = combine(scores, profile)
    shape = pl["t"].shape
    layers: dict[str, np.ndarray] = {p: pl[p] for p in ("t", "q", "r", "u", "v", "w", "gh")}
    layers.update(
        wind_speed=ws, layer_shear=shear, vertical_shear=vws, cat_ti2=ti2,
        cat_category=cat_category_codes(ti2).astype(float), icing_potential=icing_potential(pl["t"], pl["r"]),
        theta_e=theta_e, awci=composite.awci, awci_level=level_codes(composite.awci, profile).astype(float),
    )
    for module in _MODULES:
        layers[f"module_{module}"] = np.broadcast_to(np.asarray(scores[module], dtype=float), shape).copy()
    layers.update(
        t2m=sfc["2t"], d2m=sfc["2d"], rh2m=rh2m, mucape=sfc["mucape"],
        cloud_base_lcl=cloud_base_lcl_m(sfc["2t"], sfc["2d"]), precip_rate=rate,
        precip_class=precip_class_codes(rate).astype(float), precip_type=sfc["ptype"], ptype_severity=severity,
        gust_10m=sfc["10fg"], dust_proxy=dust_proxy(sfc["10fg"], rh2m), tcc=sfc["tcc"], sp_hpa=sfc["sp"] / 100.0,
    )
    for name in ("cat_category", "awci_level", "precip_class"):
        layers[name] = np.where(layers[name] < 0, np.nan, layers[name])
    return layers
