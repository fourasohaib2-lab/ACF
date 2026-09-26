"""
IFS ENS probabilities and spread for AWCI Web (spec SP5).

Each perturbed member goes through the unchanged deterministic pipeline (acf.awci.ops.pipeline.compute_step,
same relief and profiles); only events defined elsewhere in ACF are counted, no new threshold:

- p_awci_high: AWCI >= lower bound of the operational profile's "High" class;
- p_cloud_bkn: level cloud fraction >= 5/8 (broken, WMO code table 2700);
- p_icing: icing potential = 1;  p_cat_moderate: Ellrod TI2 category >= moderate (2);
- p_convection: convective class >= TCU (2), i.e. convection realised (cloud profile 1.2.0);
- p_ceiling_1500ft: ICAO ceiling below 1500 ft = 457.2 m (no ceiling = no event).

Counts are exact (integers) with the number of members holding a finite value per cell ("n"): the probability
count / n is never computed over an empty set. AWCI spread is the sample standard deviation (ddof = 1).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from acf.awci.ops.engine import Profile

CEILING_1500FT_M = 1500 * 0.3048  # ICAO Annex 2 VMC ceiling in a control zone, 1 ft = 0.3048 m
BKN_FRACTION = 5 / 8
ENS_LEVEL_PRODUCTS = ("p_awci_high", "p_cloud_bkn", "p_icing", "p_cat_moderate")
ENS_SURFACE_PRODUCTS = ("p_convection", "p_ceiling_1500ft")
ENS_STATISTICS = ("awci_mean", "awci_std")


def class_lower_bound(profile: Profile, label: str) -> float:
    """Lower AWCI bound of a class: the upper bound of the class below it (profile level_thresholds)."""
    lower = 0.0
    for upper, name in profile.level_thresholds:
        if name == label:
            return lower
        lower = upper
    raise ValueError(f"AWCI class {label!r} not in the profile")


def _events(layers: dict[str, np.ndarray], awci_high: float) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """(event, valid) per product for one member; NaN is not valid, except the ceiling where NaN = none."""
    def finite(name: str) -> np.ndarray:
        return np.isfinite(layers[name])

    with np.errstate(invalid="ignore"):
        ceiling = layers["ceiling_m"]
        return {
            "p_awci_high": (layers["awci"] >= awci_high, finite("awci")),
            "p_cloud_bkn": (layers["cloud_fraction"] >= BKN_FRACTION, finite("cloud_fraction")),
            "p_icing": (layers["icing_potential"] >= 1, finite("icing_potential")),
            "p_cat_moderate": (layers["cat_category"] >= 2, finite("cat_category")),
            "p_convection": (layers["convective_class"] >= 2, finite("convective_class")),
            "p_ceiling_1500ft": (np.isfinite(ceiling) & (ceiling < CEILING_1500FT_M), np.ones(ceiling.shape, bool)),
        }


@dataclass
class EnsembleAccumulator:
    level_shape: tuple[int, ...]
    surface_shape: tuple[int, ...]
    awci_high: float
    members: int = 0
    _count: dict[str, np.ndarray] = field(default_factory=dict)
    _n: dict[str, np.ndarray] = field(default_factory=dict)
    _sum: np.ndarray | None = None
    _sumsq: np.ndarray | None = None
    _k: np.ndarray | None = None

    def __post_init__(self) -> None:
        for name in ENS_LEVEL_PRODUCTS:
            self._count[name] = np.zeros(self.level_shape, np.uint16)
            self._n[name] = np.zeros(self.level_shape, np.uint16)
        for name in ENS_SURFACE_PRODUCTS:
            self._count[name] = np.zeros(self.surface_shape, np.uint16)
            self._n[name] = np.zeros(self.surface_shape, np.uint16)
        self._sum = np.zeros(self.level_shape)
        self._sumsq = np.zeros(self.level_shape)
        self._k = np.zeros(self.level_shape, np.uint16)

    def add(self, layers: dict[str, np.ndarray]) -> None:
        """Count one member's events (its layers are not kept)."""
        for name, (event, valid) in _events(layers, self.awci_high).items():
            self._count[name] += event & valid
            self._n[name] += valid
        awci = layers["awci"]
        ok = np.isfinite(awci)
        value = np.where(ok, awci, 0.0)
        assert self._sum is not None and self._sumsq is not None and self._k is not None
        self._sum += value
        self._sumsq += value * value
        self._k += ok
        self.members += 1

    def result(self) -> dict[str, Any]:
        assert self._sum is not None and self._sumsq is not None and self._k is not None
        out: dict[str, Any] = {"members": self.members}
        for name in (*ENS_LEVEL_PRODUCTS, *ENS_SURFACE_PRODUCTS):
            out[f"{name}_count"] = self._count[name].astype(np.uint8)
            out[f"{name}_n"] = self._n[name].astype(np.uint8)
        k = self._k.astype(float)
        with np.errstate(invalid="ignore", divide="ignore"):
            mean = np.where(k > 0, self._sum / k, np.nan)
            var = np.where(k > 1, (self._sumsq - k * mean * mean) / (k - 1), np.nan)
        out["awci_mean"] = mean.astype(np.float32)
        out["awci_std"] = np.sqrt(np.maximum(var, 0.0)).astype(np.float32)
        return out
