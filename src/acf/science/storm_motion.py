"""
Storm Motion
============
"""

import math


class StormMotion:
    """Storm motion calculator."""

    #: Empirical deviation magnitude (m/s) from Bunkers et al. (2000).
    BUNKERS_DEVIATION_MS = 7.5

    @staticmethod
    def calculate(
        mean_u: float,
        mean_v: float,
        deviation_u: float = 7.5,
        deviation_v: float = 7.5,
    ) -> tuple[float, float]:
        """
        Add a fixed (default 7.5, 7.5 m/s) offset to the mean wind.

        NOTE (correction): despite this method's docstring previously
        claiming "Approximate Bunkers storm motion", it does not
        implement the Bunkers et al. (2000) method at all - real
        Bunkers storm motion deviates from the mean wind PERPENDICULAR
        TO THE ACTUAL 0-6 km SHEAR VECTOR (see calculate_bunkers()
        below), a direction that varies case by case. This function
        instead adds the same fixed (deviation_u, deviation_v) offset
        regardless of any shear information - with the defaults, that
        is a fixed north-eastward nudge that is only physically correct
        by coincidence, for whatever specific shear orientation happens
        to make the true perpendicular-to-shear deviation equal
        (7.5, 7.5) m/s. No production caller currently depends on this
        method's exact values (verified via search - test coverage
        only asserted the trivial arithmetic itself), so this closes a
        latent landmine rather than an active bug. Kept for backward
        compatibility (the addition itself is not wrong, just not
        "Bunkers"); use calculate_bunkers() for genuine Bunkers (2000)
        storm motion from a real shear vector.

        Parameters
        ----------
        mean_u, mean_v : float
            Mean wind components (m/s), typically 0-6 km mean wind.
        deviation_u, deviation_v : float
            Fixed offset added to the mean wind (m/s). Defaults to
            (7.5, 7.5) m/s for backward compatibility only - this is
            NOT derived from any wind shear and does not represent a
            genuine Bunkers deviation in general.

        Returns
        -------
        tuple[float, float]
            (storm_u, storm_v) = (mean_u + deviation_u, mean_v + deviation_v).
        """

        storm_u = mean_u + deviation_u
        storm_v = mean_v + deviation_v

        return storm_u, storm_v

    @staticmethod
    def calculate_bunkers(
        mean_u: float,
        mean_v: float,
        shear_u: float,
        shear_v: float,
    ) -> dict[str, tuple[float, float]]:
        """
        Genuine Bunkers et al. (2000) "Internal Dynamics" storm motion.

        The right- and left-mover deviations are perpendicular to the
        0-6 km bulk shear vector, not a fixed offset: the mean wind is
        displaced by a fixed magnitude D = 7.5 m/s along the shear
        vector rotated 90 degrees (clockwise for the right mover,
        counter-clockwise - i.e. the opposite direction - for the left
        mover). Rotating a vector (x, y) by -90 degrees (clockwise)
        gives (y, -x).

        Parameters
        ----------
        mean_u, mean_v : float
            0-6 km (pressure- or density-weighted) mean wind components (m/s).
        shear_u, shear_v : float
            0-6 km bulk shear vector components (m/s), i.e.
            wind(6 km) - wind(surface) (or the mean 5.5-6 km wind minus
            the mean 0-0.5 km wind for the operational definition).
            Must be non-zero - the deviation direction is undefined for
            a zero shear vector.

        Returns
        -------
        dict
            {"right_mover": (u, v), "left_mover": (u, v)} storm motion
            vectors (m/s).

        Raises
        ------
        ValueError
            If the shear vector has zero magnitude.

        Reference
        ---------
        Bunkers, M. J., Klimowski, B. A., Zeitler, J. W., Thompson,
        R. L., & Weisman, M. L. (2000). "Predicting Supercell Motion
        Using a New Hodograph Technique". Weather and Forecasting,
        15(1), 61-79. D = 7.5 m/s per this reference; the same
        formulation is used operationally by e.g. MetPy's
        bunkers_storm_motion() and SHARPpy.
        """
        shear_mag = math.hypot(shear_u, shear_v)
        if shear_mag == 0.0:
            raise ValueError("shear vector must be non-zero - deviation direction is undefined.")

        shear_hat_u = shear_u / shear_mag
        shear_hat_v = shear_v / shear_mag

        # 90-degree clockwise rotation of the unit shear vector: (x, y) -> (y, -x).
        dev_u = StormMotion.BUNKERS_DEVIATION_MS * shear_hat_v
        dev_v = StormMotion.BUNKERS_DEVIATION_MS * (-shear_hat_u)

        right_mover = (mean_u + dev_u, mean_v + dev_v)
        left_mover = (mean_u - dev_u, mean_v - dev_v)

        return {"right_mover": right_mover, "left_mover": left_mover}
