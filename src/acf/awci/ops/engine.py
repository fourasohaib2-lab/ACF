"""
Vectorized AWCI engine.

Profile "legacy": exactly the mechanism and constants of AWCICalculator
(read from that class, not copied) - parity-tested.
Profile "operational-v1" (config/awci/profiles/operational-v1.json):
- dynamic       = 0.5 norm_wind(wind_speed) + 0.5 norm_wind_shear(layer_shear)
- thermodynamic = norm_theta_e(theta_e)          (replaces raw temperature)
- convective    = norm_cape(mucape)              (CIN no longer adds complexity)
- microphysical = 0.5 norm_precip(rate) + 0.5 ptype severity
- topographic   = norm_topographic(elevation)
- temporal, confidence: not fed in V1 -> None
Composite: awci = 100 * (sum w_m s_m + sum w_i prod s) / (sum present w_m + sum present w_i);
an interaction is present only if all its modules are; awci = NaN when sum present w_m < min_present_weight.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from acf.awci.calculator import AWCICalculator
from acf.awci.weights import WeightsManager

REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_OPERATIONAL_PROFILE_PATH = REPO_ROOT / "config" / "awci" / "profiles" / "operational-v1.json"


@dataclass(frozen=True)
class Profile:
    name: str
    version: str
    weights: dict[str, float]
    interaction_terms: dict[str, tuple[str, ...]]
    interaction_weights: dict[str, float]
    level_thresholds: tuple[tuple[float, str], ...]
    min_present_weight: float


def legacy_profile() -> Profile:
    return Profile(
        name="legacy",
        version="calculator",
        weights=dict(WeightsManager.DEFAULT_WEIGHTS),
        interaction_terms=dict(AWCICalculator.INTERACTION_TERMS),
        interaction_weights=dict(AWCICalculator.INTERACTION_WEIGHTS),
        level_thresholds=AWCICalculator.LEVEL_THRESHOLDS,
        min_present_weight=0.0,
    )


def load_profile(path: Path | str) -> Profile:
    payload: dict[str, Any] = json.loads(Path(path).read_text(encoding="utf-8"))
    profile = Profile(
        name=payload["name"],
        version=payload["version"],
        weights={k: float(v) for k, v in payload["weights"].items()},
        interaction_terms={k: tuple(v) for k, v in payload["interaction_terms"].items()},
        interaction_weights={k: float(v) for k, v in payload["interaction_weights"].items()},
        level_thresholds=tuple(
            (float("inf") if bound is None else float(bound), label) for bound, label in payload["level_thresholds"]
        ),
        min_present_weight=float(payload["min_present_weight"]),
    )
    AWCICalculator(  # reuse the calculator's own validation, never reimplemented
        weights=profile.weights,
        interaction_terms=profile.interaction_terms,
        interaction_weights=profile.interaction_weights,
        level_thresholds=profile.level_thresholds,
    )
    return profile


def _clip01(x: np.ndarray, lo: float, hi: float) -> np.ndarray:
    return (np.clip(np.asarray(x, dtype=float), lo, hi) - lo) / (hi - lo)


def legacy_module_scores(inputs: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    shape = np.shape(next(iter(inputs.values())))

    def get(key: str, default: float) -> np.ndarray:
        return np.asarray(inputs.get(key, np.full(shape, default)), dtype=float)

    zeros = np.zeros(shape)
    scores = {
        "dynamic": _clip01(get("wind_speed", 0.0), 0.0, 50.0),
        "thermodynamic": 0.5 * _clip01(get("temperature", 273.15) - 273.15, -30.0, 50.0)
        + 0.5 * _clip01(get("specific_humidity", 0.001), 0.0, 0.03),
        "convective": 0.7 * _clip01(get("cape", 0.0), 0.0, 5000.0) + 0.3 * _clip01(np.abs(get("cin", 0.0)), 0.0, 500.0),
        "microphysical": _clip01(get("precipitation", 0.0), 0.0, 50.0),
        "topographic": _clip01(get("altitude", 0.0), 0.0, 3000.0),
        "temporal": _clip01(get("temporal_change", 0.0), 0.0, 20.0),
        "confidence": 1.0 - _clip01(get("confidence", 100.0), 0.0, 100.0),
    }
    for module in ("ensemble_spread", "model_disagreement", "ceiling", "visibility", "dust", "ash", "microburst"):
        scores[module] = zeros.copy()
    return scores


def operational_module_scores(
    *,
    wind_speed: np.ndarray,
    layer_shear: np.ndarray,
    theta_e: np.ndarray,
    mucape: np.ndarray,
    precip_rate: np.ndarray,
    ptype_severity: np.ndarray,
    elevation: np.ndarray,
) -> dict[str, np.ndarray | None]:
    return {
        "dynamic": 0.5 * _clip01(wind_speed, 0.0, 50.0) + 0.5 * _clip01(layer_shear, 0.0, 50.0),
        "thermodynamic": _clip01(theta_e, 250.0, 380.0),
        "convective": _clip01(mucape, 0.0, 5000.0),
        "microphysical": 0.5 * _clip01(precip_rate, 0.0, 50.0) + 0.5 * np.clip(np.asarray(ptype_severity, dtype=float), 0.0, 1.0),
        "topographic": _clip01(elevation, 0.0, 3000.0),
        "temporal": None,
        "confidence": None,
    }


@dataclass
class CompositeResult:
    awci: np.ndarray
    decomposition: dict[str, np.ndarray]
    present_weight: np.ndarray


def combine(module_scores: dict[str, np.ndarray | None], profile: Profile) -> CompositeResult:
    arrays = [a for a in module_scores.values() if a is not None]
    shape = np.broadcast_shapes(*(np.shape(a) for a in arrays))
    weighted: dict[str, np.ndarray] = {}
    budget = np.zeros(shape)
    present_weight = np.zeros(shape)
    total = np.zeros(shape)
    for module, weight in profile.weights.items():
        score = module_scores.get(module)
        if score is None or weight == 0.0:
            weighted[module] = np.full(shape, np.nan if score is None else 0.0)
            continue
        score = np.broadcast_to(np.asarray(score, dtype=float), shape)
        present = np.isfinite(score)
        contrib = np.where(present, weight * score, np.nan)
        weighted[module] = contrib
        total += np.nan_to_num(contrib)
        budget += present * weight
        present_weight += present * weight
    for term, modules in profile.interaction_terms.items():
        weight = profile.interaction_weights[term]
        parts = [module_scores.get(m) for m in modules]
        if any(p is None for p in parts):
            weighted[term] = np.full(shape, np.nan)
            continue
        product = np.ones(shape)
        for part in parts:
            product = product * np.broadcast_to(np.asarray(part, dtype=float), shape)
        present = np.isfinite(product)
        contrib = np.where(present, weight * product, np.nan)
        weighted[term] = contrib
        total += np.nan_to_num(contrib)
        budget += present * weight
    with np.errstate(divide="ignore", invalid="ignore"):
        awci = np.where((budget > 0) & (present_weight >= profile.min_present_weight), 100.0 * total / budget, np.nan)
        decomposition = {k: 100.0 * v / budget for k, v in weighted.items()}
    return CompositeResult(awci=awci, decomposition=decomposition, present_weight=present_weight)


def level_codes(awci: np.ndarray, profile: Profile) -> np.ndarray:
    bounds = np.asarray([b for b, _ in profile.level_thresholds[:-1]])
    awci = np.asarray(awci, dtype=float)
    codes = np.searchsorted(bounds, np.nan_to_num(awci), side="right").astype(np.int8)
    return np.where(np.isfinite(awci), codes, np.int8(-1)).astype(np.int8)
