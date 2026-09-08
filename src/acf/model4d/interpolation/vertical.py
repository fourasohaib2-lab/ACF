"""
Atmospheric Complexity Framework (ACF)

MODEL4D - Vertical Interpolation
================================
Utilities for interpolating atmospheric variables across vertical coordinates
(height, geopotential height, pressure, log-pressure, eta/hybrid levels).
"""

from __future__ import annotations

import math
from typing import Sequence

import numpy as np


class VerticalInterpolation:
    """
    Performs vertical interpolation between pressure levels, geometric heights, and hybrid sigma-pressure coordinates.
    """

    @staticmethod
    def interpolate_linear(z0: float, v0: float, z1: float, v1: float, z: float) -> float:
        """
        Linearly interpolates variable between two heights z0 and z1.
        """
        if z0 == z1:
            raise ValueError("z0 and z1 cannot be equal.")
        return v0 + (z - z0) * (v1 - v0) / (z1 - z0)

    @staticmethod
    def interpolate_log_pressure(p0: float, v0: float, p1: float, v1: float, p: float) -> float:
        """
        Interpolates variable linearly in log(p), consistent with hydrostatic balance and barometric profiles.
        """
        if p0 <= 0 or p1 <= 0 or p <= 0:
            raise ValueError("Pressures must be positive.")
        if p0 == p1:
            raise ValueError("p0 and p1 cannot be equal.")

        log_p0, log_p1, log_p = math.log(p0), math.log(p1), math.log(p)
        return v0 + (log_p - log_p0) * (v1 - v0) / (log_p1 - log_p0)

    @staticmethod
    def interpolate_profile(
        levels: Sequence[float],
        values: Sequence[float] | np.ndarray,
        target_level: float,
        log_coord: bool = False,
    ) -> float | np.ndarray:
        """
        Interpolates an atmospheric vertical column profile to target_level.
        """
        lev_arr = np.asarray(levels, dtype=float)
        vals_arr = np.asarray(values)

        if len(lev_arr) < 2:
            raise ValueError("At least two vertical levels are required.")
        if len(lev_arr) != len(vals_arr):
            raise ValueError("Length of levels and values must match.")

        if log_coord:
            if np.any(lev_arr <= 0) or target_level <= 0:
                raise ValueError("Levels and target_level must be positive for log interpolation.")
            coords = np.log(lev_arr)
            target_coord = math.log(target_level)
        else:
            coords = lev_arr
            target_coord = target_level

        # Handle ascending vs descending levels
        if coords[0] > coords[-1]:
            coords = coords[::-1]
            vals_arr = vals_arr[::-1]

        if target_coord <= coords[0]:
            return vals_arr[0]
        if target_coord >= coords[-1]:
            return vals_arr[-1]

        idx = int(np.searchsorted(coords, target_coord))
        c0, c1 = coords[idx - 1], coords[idx]
        v0, v1 = vals_arr[idx - 1], vals_arr[idx]
        alpha = (target_coord - c0) / (c1 - c0)
        return v0 + alpha * (v1 - v0)

