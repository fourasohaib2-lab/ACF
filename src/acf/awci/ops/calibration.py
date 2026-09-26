"""
Reproducible calibration of the critical relative humidity RHc per etage (Sundqvist scheme).

Coordinate descent, etage by etage (low -> mid -> high, `passes` times), on a fixed grid of
candidate values: minimise the mean squared error between the maximum-random total cover
diagnosed from IFS r and the IFS total cloud cover tcc, over every finite cell supplied.
The IFS tcc is a model product, not an observation: the calibration makes the diagnosed
layers consistent with the IFS cloud scheme; validation against METAR remains separate.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any

import numpy as np

from acf.awci.ops.cloud_profile import CloudProfile
from acf.awci.ops.clouds import ETAGE_NAMES, etage_codes, level_cloud_fraction, max_random_cover

DEFAULT_GRID = np.round(np.arange(0.50, 0.951, 0.025), 3)


def _cover(r_pct: np.ndarray, etage: np.ndarray, underground: np.ndarray, profile: CloudProfile) -> np.ndarray:
    fraction = np.where(underground, np.nan, level_cloud_fraction(r_pct, etage, profile))
    return max_random_cover(fraction)


def _rmse(cover: np.ndarray, tcc: np.ndarray) -> tuple[float, float, int]:
    ok = np.isfinite(cover) & np.isfinite(tcc)
    diff = cover[ok] - tcc[ok]
    return float(np.sqrt(np.mean(diff**2))), float(np.mean(diff)), int(ok.sum())


def calibrate_rhc(
    r_pct: np.ndarray, sp_hpa: np.ndarray, levels_hpa: np.ndarray, tcc: np.ndarray, profile: CloudProfile,
    grid: np.ndarray = DEFAULT_GRID, passes: int = 3,
) -> dict[str, Any]:
    """r_pct (n, level, lat, lon), sp_hpa and tcc (n, lat, lon): n independent samples (steps, runs)."""
    r_pct, sp_hpa, tcc = (np.asarray(a, dtype=float) for a in (r_pct, sp_hpa, tcc))
    levels = np.asarray(levels_hpa, dtype=float)
    etages = np.stack([etage_codes(levels, sp, profile) for sp in sp_hpa])
    underground = levels[None, :, None, None] > sp_hpa[:, None]

    def score(candidate: CloudProfile) -> tuple[float, float, int]:
        cover = np.stack([_cover(r_pct[n], etages[n], underground[n], candidate) for n in range(len(r_pct))])
        return _rmse(cover, tcc)

    before, _, n_cells = score(profile)
    best = profile
    for _ in range(passes):
        for name in ETAGE_NAMES:
            trials = [replace(best, rh_critical={**best.rh_critical, name: float(v)}) for v in grid]
            errors = [score(t)[0] for t in trials]
            best = trials[int(np.argmin(errors))]
    after, bias, _ = score(best)
    return {"rh_critical": dict(best.rh_critical), "rmse_before": round(before, 4), "rmse_after": round(after, 4),
            "bias_after": round(bias, 4), "n_cells": n_cells}
