"""
Domain indicators of one (run, step, level) for the AWCI Web KPI row (SP2 spec §5.1).

Area percentages and percentiles are weighted by grid-cell area: on the regular lat/lon grid of a
spherical Earth a cell's area is proportional to cos(latitude), so a 0.25° cell at 45°N counts for
0.71 of one at the equator. Cells without data (NaN: below ground, missing input) are excluded from
numerator and denominator. Badge thresholds are ACF choices (status HYPOTHESIS), served by /registry.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from acf.awci.ops.engine import Profile, level_codes

AREA_BADGES_PCT = (5.0, 15.0, 30.0)
SHEAR_BADGES_PER_S = (5e-3, 8e-3)
CONVECTIVE_MUCAPE_J_KG = 1000.0
IFR_CEILING_M = 304.8  # 1000 ft (1 ft = 0.3048 m exactly)
SUMMARY_THRESHOLDS: dict[str, Any] = {
    "area_badges_pct": AREA_BADGES_PCT, "shear_badges_per_s": SHEAR_BADGES_PER_S,
    "convective_mucape_j_kg": CONVECTIVE_MUCAPE_J_KG, "low_ceiling_m": IFR_CEILING_M,
    "status": "HYPOTHESIS", "weighting": "cell area, cos(latitude)",
}
_NAMES = ("ok", "attention", "serious", "critical")


def area_weights(lats: np.ndarray, nx: int) -> np.ndarray:
    return np.cos(np.radians(np.asarray(lats, dtype=float)))[:, None] * np.ones((1, nx))


def area_pct(condition: np.ndarray, valid: np.ndarray, weights: np.ndarray) -> float | None:
    total = float(weights[valid].sum())
    return None if total <= 0.0 else 100.0 * float(weights[valid & condition].sum()) / total


def weighted_percentile(values: np.ndarray, weights: np.ndarray, q: float) -> float | None:
    ok = np.isfinite(values)
    if not ok.any():
        return None
    v, w = values[ok], weights[ok]
    order = np.argsort(v)
    cdf = np.cumsum(w[order])
    idx = min(int(np.searchsorted(cdf / cdf[-1], q / 100.0)), v.size - 1)
    return float(v[order][idx])


def badge(value: float | None, bounds: tuple[float, ...]) -> str | None:
    return None if value is None else _NAMES[sum(value >= b for b in bounds)]


def _pct(layer: np.ndarray | None, weights: np.ndarray, predicate: Any) -> float | None:
    if layer is None:
        return None
    valid = np.isfinite(layer)
    with np.errstate(invalid="ignore"):
        return area_pct(predicate(layer), valid, weights)


def summarize(layers: dict[str, np.ndarray | None], lats: np.ndarray, profile: Profile) -> dict[str, Any]:
    awci = layers["awci"]
    assert awci is not None
    w = area_weights(lats, awci.shape[1])
    p95 = weighted_percentile(awci, w, 95.0)
    code = None if p95 is None else int(level_codes(np.array([p95]), profile)[0])
    bias = layers["cloud_cover_bias"]
    mucape = layers["mucape"]
    out: dict[str, Any] = {
        "awci_p95": p95, "awci_class": None if code is None else profile.level_thresholds[code][1],
        "turbulence_area_pct": _pct(layers["cat_category"], w, lambda a: a >= 2),
        "convection_area_pct": _pct(mucape, w, lambda a: a >= CONVECTIVE_MUCAPE_J_KG),
        "mucape_max": None if mucape is None or not np.isfinite(mucape).any() else float(np.nanmax(mucape)),
        "icing_area_pct": _pct(layers["icing_potential"], w, lambda a: a >= 1),
        "shear_p95": None if layers["vertical_shear"] is None else weighted_percentile(layers["vertical_shear"], w, 95.0),
        "heavy_precip_area_pct": _pct(layers["precip_class"], w, lambda a: a >= 3),
        # every cell counts: no ceiling (NaN) means no low ceiling, not missing data
        "low_ceiling_area_pct": None if layers["ceiling_m"] is None else area_pct(
            np.nan_to_num(layers["ceiling_m"], nan=np.inf) < IFR_CEILING_M, np.ones(awci.shape, dtype=bool), w),
        "cb_area_pct": _pct(layers["convective_class"], w, lambda a: a >= 3),
        "cloud_cover_bias_mean": None if bias is None or not np.isfinite(bias).any() else float(np.nanmean(bias)),
        "valid_cells_pct": area_pct(np.isfinite(awci), np.ones(awci.shape, dtype=bool), w),
    }
    out["badges"] = {
        **{k: badge(out[k], AREA_BADGES_PCT) for k in ("turbulence_area_pct", "convection_area_pct", "icing_area_pct",
                                                       "heavy_precip_area_pct", "low_ceiling_area_pct", "cb_area_pct")},
        "shear_p95": badge(out["shear_p95"], SHEAR_BADGES_PER_S),
    }
    return out
