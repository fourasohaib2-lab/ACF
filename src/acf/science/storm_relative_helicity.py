"""
Storm Relative Helicity (SRH)
=============================
"""

from collections.abc import Sequence


class StormRelativeHelicity:
    """Storm Relative Helicity calculator."""

    @staticmethod
    def calculate_profile(
        u: Sequence[float],
        v: Sequence[float],
        storm_u: float,
        storm_v: float,
    ) -> float:
        """
        Compute SRH over a full wind profile (multi-layer), the
        practical form used operationally for a chosen depth (e.g.
        0-1 km or 0-3 km): sum the single-layer kernel over every
        layer between consecutive levels.

            SRH = sum_i [ (u_i - cu)*(v_{i+1}-v_i) - (v_i - cv)*(u_{i+1}-u_i) ]

        This is the discretized form of SRH = -integral (V-C) x (dV/dz) dz.

        Parameters
        ----------
        u, v : sequence of float
            Wind components (m/s) at each level, surface-to-top order,
            same length, at least 2 levels.
        storm_u, storm_v : float
            Storm motion vector components (m/s).

        Returns
        -------
        float
            SRH (m^2/s^2) over the full depth spanned by the profile.

        Raises
        ------
        ValueError
            If u and v have inconsistent lengths or fewer than 2 levels.

        Reference
        ---------
        Davies-Jones, R., Burgess, D., & Foster, M. (1990). "Test of
        Helicity as a Tornado Forecast Parameter". Preprints, 16th
        Conf. on Severe Local Storms, AMS.
        """
        n = len(u)
        if len(v) != n:
            raise ValueError("u and v must have the same length.")
        if n < 2:
            raise ValueError("at least two levels are required.")

        srh = 0.0
        for i in range(n - 1):
            du = u[i + 1] - u[i]
            dv = v[i + 1] - v[i]
            srh += (u[i] - storm_u) * dv - (v[i] - storm_v) * du

        return srh

    @staticmethod
    def calculate(
        u: float,
        v: float,
        storm_u: float,
        storm_v: float,
        du: float,
        dv: float,
    ) -> float:
        """
        Compute SRH for a single layer.

        SRH = (u-cu) * dv - (v-cv) * du

        See calculate_profile() for the multi-layer (full wind
        profile) version used operationally over a chosen depth.
        """

        return (u - storm_u) * dv - (v - storm_v) * du

    @staticmethod
    def category(value: float) -> str:
        """
        SRH classification.
        """

        if value < 100:
            return "Weak"

        if value < 250:
            return "Moderate"

        if value < 400:
            return "Strong"

        return "Extreme"
