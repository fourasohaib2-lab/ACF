"""
Calibration of the convective (TCU/Cb) diagnosis against METAR, reproducible and out-of-sample.

The current rule (acf.awci.ops.clouds.convective_diagnosis: class >= TCU) over-forecasts convection
(frequency bias 4.15 on IFS 2026-09-25 12Z). Only *stricter* rules are considered: the current rule AND
extra conditions on IFS quantities that indicate convection actually realised by the model, all stored in
the cube:

- mucape (J/kg): stronger instability than the current 100 J/kg floor;
- column_condensate (kg/m2, tcw - tcwv): a convective column holds condensate;
- precip_rate (mm/h, IFS tprate): the IFS convection scheme precipitates when it is active.

Only quantities the diagnosis itself receives are candidates (acf.awci.ops.cloud_profile._REALISED), so the
selected rule is applied exactly as evaluated. The OLR top temperature is left out: it is not a diagnosis
input and is undefined at step 0 (no previous accumulation).

Selection: among the candidate rules whose frequency bias lies in `bias_range`, the one with the highest
Equitable Threat Score (Jolliffe & Stephenson 2012), ties broken by the fewest conditions. It is chosen on
calibration runs and must be judged on separate test runs.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Any

import numpy as np

from acf.awci.ops.verify import scores

Rule = dict[str, tuple[str, float]]  # predictor -> (">=" | "<=", threshold)


@dataclass
class ConvectiveSample:
    observed: np.ndarray  # METAR convection (TCU/CB/TS), known pairs only
    base: np.ndarray  # current diagnosis: convective_class >= TCU
    predictors: dict[str, np.ndarray]


def forecast(sample: ConvectiveSample, rule: Rule) -> np.ndarray:
    event = sample.base.copy()
    for name, (op, threshold) in rule.items():
        values = sample.predictors[name]
        with np.errstate(invalid="ignore"):
            event &= (values >= threshold) if op == ">=" else (values <= threshold)  # NaN never satisfies
    return event


def evaluate(sample: ConvectiveSample, rule: Rule) -> dict[str, Any]:
    f, o = forecast(sample, rule), sample.observed
    return scores(int(np.sum(f & o)), int(np.sum(f & ~o)), int(np.sum(~f & o)), int(np.sum(~f & ~o)))


def candidate_rules() -> list[Rule]:
    """Small grid of physically interpretable thresholds (every combination, None = condition absent)."""
    grid: dict[str, tuple[str, list[float | None]]] = {
        "mucape": (">=", [None, 250.0, 500.0, 1000.0]),
        "column_condensate": (">=", [None, 0.1, 0.3]),
        "precip_rate": (">=", [None, 0.1, 0.5]),
    }
    rules = []
    for combo in itertools.product(*(values for _, values in grid.values())):
        rules.append({name: (grid[name][0], float(v)) for name, v in zip(grid, combo) if v is not None})
    return rules


def select_rule(sample: ConvectiveSample, rules: list[Rule],
                bias_range: tuple[float, float] = (0.7, 1.5)) -> tuple[Rule, list[dict[str, Any]]]:
    table = [{"rule": rule, **evaluate(sample, rule)} for rule in rules]
    eligible = [t for t in table if t["bias"] is not None and bias_range[0] <= t["bias"] <= bias_range[1]
                and t["ets"] is not None]
    if not eligible:
        raise ValueError(f"no candidate rule has a frequency bias within {bias_range}")
    best = max(eligible, key=lambda t: (round(t["ets"], 6), -len(t["rule"])))
    return best["rule"], table
