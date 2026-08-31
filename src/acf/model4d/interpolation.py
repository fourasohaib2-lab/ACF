"""
Atmospheric Complexity Framework (ACF)

MODEL4D - Interpolation Facade
==============================

NOTE (found, NOT changed — RÈGLE D'OR / single source of truth): this
module is dead code. `src/acf/model4d/interpolation/` is ALSO a
package with its own __init__.py, which Python's import resolution
always finds before this sibling module.py of the same name - so
`import acf.model4d.interpolation` (or `from acf.model4d.interpolation
import Interpolation4D`) can never actually reach this file, and the
package's __init__.py doesn't re-export Interpolation4D either, so
this unified facade class is permanently unreachable by any import
path. The individual interpolation classes it wraps
(BilinearInterpolation, TemporalInterpolation, VerticalInterpolation,
etc.) remain genuinely reachable and correct via the package directly
(acf.model4d.interpolation.temporal, .vertical, ...). Not deleted per
project convention - flagged so nobody mistakes this for live code.
Same situation as data/engine.py's NOTE.
"""

from __future__ import annotations

from typing import Any

from acf.model4d.interpolation.bilinear import BilinearInterpolation
from acf.model4d.interpolation.cubic import CubicInterpolation
from acf.model4d.interpolation.interpolation_engine import InterpolationEngine
from acf.model4d.interpolation.linear import LinearInterpolation
from acf.model4d.interpolation.spline import SplineInterpolation
from acf.model4d.interpolation.temporal import TemporalInterpolation
from acf.model4d.interpolation.trilinear import TrilinearInterpolation
from acf.model4d.interpolation.vertical import VerticalInterpolation


class Interpolation4D:
    """
    Unified 4D spatio-temporal interpolation interface.
    """

    def __init__(self, engine: InterpolationEngine | None = None) -> None:
        self.engine = engine or InterpolationEngine()

    def spatial_1d(self, x0: float, y0: float, x1: float, y1: float, x: float) -> float:
        return LinearInterpolation.interpolate(x0, y0, x1, y1, x)

    def spatial_2d(self, q11: float, q21: float, q12: float, q22: float, tx: float, ty: float) -> float:
        return BilinearInterpolation.interpolate(q11, q21, q12, q22, tx, ty)

    def spatial_3d(
        self,
        c000: float,
        c100: float,
        c010: float,
        c110: float,
        c001: float,
        c101: float,
        c011: float,
        c111: float,
        tx: float,
        ty: float,
        tz: float,
    ) -> float:
        return TrilinearInterpolation.interpolate(c000, c100, c010, c110, c001, c101, c011, c111, tx, ty, tz)

    def temporal(self, t0: float, v0: Any, t1: float, v1: Any, t: float) -> Any:
        return TemporalInterpolation.interpolate(t0, v0, t1, v1, t)

    def vertical(self, p0: float, v0: float, p1: float, v1: float, p: float, log_p: bool = True) -> float:
        if log_p:
            return VerticalInterpolation.interpolate_log_pressure(p0, v0, p1, v1, p)
        return VerticalInterpolation.interpolate_linear(p0, v0, p1, v1, p)


__all__ = [
    "BilinearInterpolation",
    "CubicInterpolation",
    "Interpolation4D",
    "InterpolationEngine",
    "LinearInterpolation",
    "SplineInterpolation",
    "TemporalInterpolation",
    "TrilinearInterpolation",
    "VerticalInterpolation",
]

