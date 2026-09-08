"""
Atmospheric Complexity Framework (ACF)

MODEL4D - Temporal Interpolation
================================
Utilities for interpolating atmospheric and meteorological fields along the time dimension.
"""

from __future__ import annotations

from typing import Sequence

import numpy as np


class TemporalInterpolation:
    """
    Performs temporal interpolation across model timesteps and forecast cycles.
    """

    @staticmethod
    def fraction(t0: float, t1: float, t: float) -> float:
        """
        Calculates normalized temporal fraction between t0 and t1.
        """
        if t0 == t1:
            raise ValueError("t0 and t1 cannot be equal.")
        return (t - t0) / (t1 - t0)

    @staticmethod
    def interpolate(
        t0: float,
        v0: float | np.ndarray,
        t1: float,
        v1: float | np.ndarray,
        t: float,
    ) -> float | np.ndarray:
        """
        Linearly interpolates field values between time t0 and t1.
        """
        if t0 == t1:
            raise ValueError("t0 and t1 cannot be equal.")
        alpha = (t - t0) / (t1 - t0)
        return v0 + alpha * (v1 - v0)

    @staticmethod
    def nearest(times: Sequence[float], values: Sequence[float] | np.ndarray, target_time: float) -> float | np.ndarray:
        """
        Selects field value at the closest available timestep.
        """
        times_arr = np.asarray(times)
        if len(times_arr) == 0:
            raise ValueError("Time series cannot be empty.")
        idx = int(np.argmin(np.abs(times_arr - target_time)))
        return np.asarray(values)[idx]

    @staticmethod
    def interpolate_series(
        times: Sequence[float],
        values: Sequence[float] | np.ndarray,
        target_time: float,
        method: str = "linear",
    ) -> float | np.ndarray:
        """
        Interpolates a time series of scalar or tensor fields at target_time.
        """
        times_arr = np.asarray(times, dtype=float)
        vals_arr = np.asarray(values)

        if len(times_arr) < 2:
            raise ValueError("At least two timesteps are required for interpolation.")
        if len(times_arr) != len(vals_arr):
            raise ValueError("Length of times and values must match.")

        if method == "nearest":
            return TemporalInterpolation.nearest(times, values, target_time)

        # Linear interpolation along sorted times
        if target_time <= times_arr[0]:
            return vals_arr[0]
        if target_time >= times_arr[-1]:
            return vals_arr[-1]

        idx = int(np.searchsorted(times_arr, target_time))
        t0, t1 = times_arr[idx - 1], times_arr[idx]
        v0, v1 = vals_arr[idx - 1], vals_arr[idx]
        return TemporalInterpolation.interpolate(t0, v0, t1, v1, target_time)

