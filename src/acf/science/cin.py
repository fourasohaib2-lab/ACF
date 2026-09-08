"""
Convective Inhibition (CIN)
============================

Physical formulation (parcel theory, negative buoyancy integral):

    CIN = integral of g * (Tv_env - Tv_parcel) / Tv_env dz
          over layers where the parcel is negatively buoyant.

Mirrors science/cape.py: same virtual-temperature handling, same
trapezoidal integration, same backward-compatible signature.

Reference:
    Doswell, C. A., & Rasmussen, E. N. (1994). "The Effect of
    Neglecting the Virtual Temperature Correction on CAPE Calculations".
    Weather and Forecasting, 9(4), 625-629.
"""

from collections.abc import Sequence

from acf.science.constants import G, T0
from acf.science.virtual_temperature import VirtualTemperature


class CIN:
    """Physical CIN calculator (negative buoyancy integral)."""

    @staticmethod
    def calculate(
        parcel_temperature: Sequence[float],
        environment_temperature: Sequence[float],
        height: Sequence[float],
        parcel_humidity: Sequence[float] | None = None,
        environment_humidity: Sequence[float] | None = None,
        is_kelvin: bool = False,
    ) -> float:
        """
        Compute CIN (J/kg, returned as a positive magnitude) by
        integrating negative buoyancy.

        Parameters
        ----------
        Same conventions as CAPE.calculate().

        Returns
        -------
        float
            CIN magnitude in J/kg (always >= 0). Callers that need the
            conventional negative sign should negate the result.

        Raises
        ------
        ValueError
            If profiles have inconsistent lengths or fewer than two levels.
        """
        n = len(height)
        if not (len(parcel_temperature) == len(environment_temperature) == n):
            raise ValueError("profiles must have the same length.")
        if n < 2:
            raise ValueError("at least two levels are required.")

        def to_kelvin(t: float) -> float:
            return t if is_kelvin else t + T0

        def virtual(t_k: float, q: float | None) -> float:
            return VirtualTemperature.calculate(t_k, q) if q is not None else t_k

        buoyancy_deficit = []
        for i in range(n):
            qp = parcel_humidity[i] if parcel_humidity is not None else None
            qe = environment_humidity[i] if environment_humidity is not None else None
            tv_p = virtual(to_kelvin(parcel_temperature[i]), qp)
            tv_e = virtual(to_kelvin(environment_temperature[i]), qe)
            buoyancy_deficit.append(G * (tv_e - tv_p) / tv_e)

        cin = 0.0
        for i in range(n - 1):
            dz = height[i + 1] - height[i]
            b_avg = 0.5 * (max(buoyancy_deficit[i], 0.0) + max(buoyancy_deficit[i + 1], 0.0))
            cin += b_avg * dz

        return max(cin, 0.0)
