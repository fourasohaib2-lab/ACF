"""
Versioned thresholds of the cloud diagnostics (config/awci/clouds/<name>.json).

Normative values (ICAO ceiling, 1 okta, ECMWF etage bounds) and ACF choices (status HYPOTHESIS)
live side by side; every group carries a reference in ``references``.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_CLOUD_PROFILE_PATH = REPO_ROOT / "config" / "awci" / "clouds" / "cloud-v1.json"

_CONVECTION = ("cape_min_j_kg", "cb_min_depth_m", "tcu_min_depth_m", "humilis_max_depth_m",
               "glaciation_temp_k", "capillatus_temp_k", "condensate_min_kg_m2")
_GENUS = ("st_max_base_m", "ns_min_depth_m", "as_min_depth_m", "cc_max_depth_m", "cs_min_oktas",
          "continuous_precip_mm_h")
_SPECIES = ("lenticularis_min_wind_m_s", "lenticularis_min_relief_m", "lenticularis_froude_min",
            "lenticularis_froude_max", "fractus_min_wind_m_s", "nebulosus_min_oktas", "nebulosus_max_std",
            "spissatus_min_condensate_kg_m2")


@dataclass(frozen=True)
class CloudProfile:
    name: str
    version: str
    rh_critical: dict[str, float]
    sigma_low_mid: float
    sigma_mid_high: float
    layer_min_fraction: float
    ceiling_max_base_m: float
    bias_degraded_threshold: float
    convection: dict[str, float]
    genus: dict[str, float]
    species: dict[str, float]
    references: dict[str, str]
    calibration: dict[str, Any] | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _group(raw: dict[str, Any], key: str, names: tuple[str, ...]) -> dict[str, float]:
    group = raw.get(key, {})
    missing = [n for n in names if n not in group]
    if missing:
        raise ValueError(f"cloud profile: {key} lacks {missing}")
    return {n: float(group[n]) for n in names}


def load_cloud_profile(path: Path | str = DEFAULT_CLOUD_PROFILE_PATH) -> CloudProfile:
    raw: dict[str, Any] = json.loads(Path(path).read_text(encoding="utf-8"))
    rhc = _group(raw, "rh_critical", ("low", "mid", "high"))
    if not all(0.0 < v < 1.0 for v in rhc.values()):
        raise ValueError(f"cloud profile: rh_critical must lie in (0, 1), got {rhc}")
    bounds = _group(raw, "sigma_bounds", ("low_mid", "mid_high"))
    if not 0.0 < bounds["mid_high"] < bounds["low_mid"] < 1.0:
        raise ValueError(f"cloud profile: need 0 < mid_high < low_mid < 1, got {bounds}")
    min_fraction = float(raw["layer_min_fraction"])
    if not 0.0 < min_fraction < 1.0:
        raise ValueError("cloud profile: layer_min_fraction must lie in (0, 1)")
    return CloudProfile(
        name=str(raw["name"]), version=str(raw["version"]), rh_critical=rhc,
        sigma_low_mid=bounds["low_mid"], sigma_mid_high=bounds["mid_high"], layer_min_fraction=min_fraction,
        ceiling_max_base_m=float(raw["ceiling_max_base_m"]),
        bias_degraded_threshold=float(raw["bias_degraded_threshold"]),
        convection=_group(raw, "convection", _CONVECTION), genus=_group(raw, "genus", _GENUS),
        species=_group(raw, "species", _SPECIES), references=dict(raw.get("references", {})),
        calibration=raw.get("calibration"),
    )
