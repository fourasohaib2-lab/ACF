"""
Convective Available Potential Energy (CAPE)
============================================

Physical formulation (parcel theory, buoyancy integral):

    CAPE = integral of g * (Tv_parcel - Tv_env) / Tv_env dz
           over layers where the parcel is positively buoyant.

Virtual temperature (Tv) is used when humidity profiles are supplied,
so moisture loading is accounted for; otherwise raw temperature is
used (dry-parcel approximation), which is the previous behaviour of
this module and is kept as the default so no caller is silently
changed in units it did not opt into.

Reference:
    Doswell, C. A., & Rasmussen, E. N. (1994). "The Effect of
    Neglecting the Virtual Temperature Correction on CAPE Calculations".
    Weather and Forecasting, 9(4), 625-629.
"""

from collections.abc import Sequence

from acf.science.constants import G, T0
from acf.science.virtual_temperature import VirtualTemperature


class CAPE:
    """Physical CAPE calculator (positive buoyancy integral)."""

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
        Compute CAPE (J/kg) by vertically integrating parcel buoyancy.

        Parameters
        ----------
        parcel_temperature : sequence of float
            Parcel temperature profile (°C by default, Kelvin if is_kelvin=True).
        environment_temperature : sequence of float
            Environment temperature profile, same units and levels.
        height : sequence of float
            Geometric height of each level (m), increasing with index.
        parcel_humidity : sequence of float, optional
            Parcel specific humidity profile (kg/kg). When provided
            (together with environment_humidity), virtual temperature
            is used instead of raw temperature to account for moisture
            loading (Doswell & Rasmussen, 1994).
        environment_humidity : sequence of float, optional
            Environment specific humidity profile (kg/kg).
        is_kelvin : bool
            Set True if the temperature profiles are already in Kelvin.

        Returns
        -------
        float
            CAPE in J/kg (always >= 0).

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

        buoyancy = []
        for i in range(n):
            qp = parcel_humidity[i] if parcel_humidity is not None else None
            qe = environment_humidity[i] if environment_humidity is not None else None
            tv_p = virtual(to_kelvin(parcel_temperature[i]), qp)
            tv_e = virtual(to_kelvin(environment_temperature[i]), qe)
            buoyancy.append(G * (tv_p - tv_e) / tv_e)

        cape = 0.0
        for i in range(n - 1):
            dz = height[i + 1] - height[i]
            # Trapezoidal integration restricted to the positively buoyant
            # portion of each layer (negative buoyancy contributes 0, not
            # a penalty — that is CIN's role).
            b_avg = 0.5 * (max(buoyancy[i], 0.0) + max(buoyancy[i + 1], 0.0))
            cape += b_avg * dz

        return max(cape, 0.0)
