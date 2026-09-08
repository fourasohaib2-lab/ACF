"""
Precipitation
=============

VIL (Greene & Clark 1972), WMO precipitation intensity classification,
and a hydrometeor-type heuristic. The Z-R relation (Marshall & Palmer
1948) and raindrop size distribution already exist as computable
EncyclopediaEntry objects in science/encyclopedia/radar_extended.py
and science/encyclopedia/precipitation.py (calculate_radar_reflectivity_z,
calculate_rain_rate_from_z, calculate_marshall_palmer_nd) — reused
here, not duplicated.

NOT implemented here (documented gap, not fabricated): MEHS (Maximum
Expected/Estimated Hail Size) and POH/POSH (Probability of Severe
Hail), Witt et al. (1998). Verified the algorithm's *structure* (SHI =
height/temperature-weighted integral of a hail kinetic energy flux
Ė(Z) from the melting level to storm top, with a 40-50 dBZ transition
weighting function, then POSH/MESH are regressions on SHI) via
multiple searches, but could not obtain the exact numeric
coefficients (Ė(Z) flux equation, W(Z) transition function, SHI->
POSH/MESH regression constants) with confidence — sources gave
inconsistent or incomplete numbers. Implementing this with guessed
constants would misrepresent a specific, named, operationally-used
algorithm as validated when it isn't. Flagged for future work with a
verified primary source (the original Witt et al. 1998 Wea.
Forecasting paper).

Reference:
    Greene, D. R., & Clark, R. A. (1972). "Vertically Integrated
    Liquid Water — A New Analysis Tool". Mon. Wea. Rev., 100(7), 548-552.
"""

from acf.science.encyclopedia.radar_extended import calculate_radar_reflectivity_z, calculate_rain_rate_from_z

# WMO rain intensity classification thresholds (mm/h).
_INTENSITY_THRESHOLDS = [
    (0.1, "Trace"),
    (2.5, "Light"),
    (7.6, "Moderate"),
    (50.0, "Heavy"),
]
_INTENSITY_VIOLENT = "Violent"

ECHO_TOP_THRESHOLD_DBZ = 18.0


class VIL:
    """Vertically Integrated Liquid water content (Greene & Clark 1972)."""

    @staticmethod
    def layer_liquid_water_density(reflectivity_mm6_m3: float) -> float:
        """
        M = 3.44e-6 * Ze^(4/7)

        Parameters
        ----------
        reflectivity_mm6_m3 : float
            Equivalent radar reflectivity factor Ze (mm^6/m^3, linear
            — not dBZ), >= 0.

        Returns
        -------
        float
            Liquid water density M (kg/m^3, or g/m^3 x 1e-3 — Greene &
            Clark's original units; see layer_vil() for the
            path-integrated kg/m^2 quantity actually called "VIL").

        Reference
        ---------
        Greene & Clark (1972), Mon. Wea. Rev., 100(7), 548-552.
        """
        if reflectivity_mm6_m3 < 0:
            raise ValueError("reflectivity_mm6_m3 must be non-negative.")
        return 3.44e-6 * reflectivity_mm6_m3 ** (4.0 / 7.0)

    @staticmethod
    def calculate(reflectivity_profile_mm6_m3: list[float], height_profile_m: list[float]) -> float:
        """
        VIL = sum_i [ 0.5 * (M_i + M_(i+1)) * (h_(i+1) - h_i) ]

        Trapezoidal vertical integration of the layer liquid water
        density between consecutive reflectivity observations.

        Parameters
        ----------
        reflectivity_profile_mm6_m3 : list of float
            Equivalent reflectivity Ze at each height level (mm^6/m^3,
            linear), same length as height_profile_m, >= 2 levels.
        height_profile_m : list of float
            Heights of each level (m), strictly increasing.

        Returns
        -------
        float
            VIL (kg/m^2).

        Raises
        ------
        ValueError
            If profiles have inconsistent lengths or fewer than 2 levels.
        """
        n = len(reflectivity_profile_mm6_m3)
        if len(height_profile_m) != n:
            raise ValueError("reflectivity and height profiles must have the same length.")
        if n < 2:
            raise ValueError("at least two levels are required.")

        densities = [VIL.layer_liquid_water_density(z) for z in reflectivity_profile_mm6_m3]

        vil = 0.0
        for i in range(n - 1):
            dh = height_profile_m[i + 1] - height_profile_m[i]
            vil += 0.5 * (densities[i] + densities[i + 1]) * dh
        return vil


class EchoTop:
    """Radar echo top height."""

    @staticmethod
    def height(
        reflectivity_profile_dbz: list[float],
        height_profile_m: list[float],
        threshold_dbz: float = ECHO_TOP_THRESHOLD_DBZ,
    ) -> float:
        """
        Echo top height: the highest altitude at which reflectivity
        still meets or exceeds threshold_dbz (conventionally 18 dBZ).
        Linear interpolation between the last level above threshold
        and the first level below it.

        Parameters
        ----------
        reflectivity_profile_dbz : list of float
            Reflectivity (dBZ) at each height level, surface-to-top
            order, same length as height_profile_m, >= 2 levels.
        height_profile_m : list of float
            Heights (m), strictly increasing.
        threshold_dbz : float
            Echo top threshold (dBZ). Defaults to the conventional 18 dBZ.

        Returns
        -------
        float
            Echo top height (m). Returns 0.0 if no level reaches the
            threshold; returns the profile top if the threshold is
            still exceeded at the highest supplied level (a real
            limitation of finite input data, not hidden).

        Raises
        ------
        ValueError
            If profiles have inconsistent lengths or fewer than 2 levels.
        """
        n = len(reflectivity_profile_dbz)
        if len(height_profile_m) != n:
            raise ValueError("reflectivity and height profiles must have the same length.")
        if n < 2:
            raise ValueError("at least two levels are required.")

        if reflectivity_profile_dbz[0] < threshold_dbz:
            return 0.0

        for i in range(n - 1):
            if reflectivity_profile_dbz[i] >= threshold_dbz and reflectivity_profile_dbz[i + 1] < threshold_dbz:
                z_below, z_above = reflectivity_profile_dbz[i], reflectivity_profile_dbz[i + 1]
                h_below, h_above = height_profile_m[i], height_profile_m[i + 1]
                frac = (threshold_dbz - z_below) / (z_above - z_below)
                return h_below + frac * (h_above - h_below)

        return height_profile_m[-1]


class PrecipitationIntensity:
    """WMO rain intensity classification."""

    @staticmethod
    def classify(rate_mm_h: float) -> str:
        """
        Classify a rain rate per WMO conventional thresholds.

        Parameters
        ----------
        rate_mm_h : float
            Precipitation rate (mm/h), >= 0.

        Returns
        -------
        str
            "Trace" (<0.1), "Light" (0.1-2.5), "Moderate" (2.5-7.6),
            "Heavy" (7.6-50), "Violent" (>50).
        """
        if rate_mm_h < 0:
            raise ValueError("rate_mm_h must be non-negative.")

        for threshold, label in _INTENSITY_THRESHOLDS:
            if rate_mm_h < threshold:
                return label
        return _INTENSITY_VIOLENT

    @staticmethod
    def rain_rate_from_reflectivity_dbz(reflectivity_dbz: float, a: float = 200.0, b: float = 1.6) -> float:
        """
        Convenience: rain rate directly from reflectivity (dBZ), via
        the existing Marshall-Palmer Z-R relation (not reimplemented).
        """
        return calculate_rain_rate_from_z(reflectivity_dbz, a, b)

    @staticmethod
    def reflectivity_from_rain_rate(rate_mm_h: float, a: float = 200.0, b: float = 1.6) -> float:
        """
        Convenience: reflectivity (mm^6/m^3, linear) from a rain rate,
        via the existing Marshall-Palmer Z-R relation (not reimplemented).
        """
        return calculate_radar_reflectivity_z(rate_mm_h, a, b)


class HydrometeorType:
    """
    Surface precipitation phase from wet-bulb temperature — a
    heuristic forecasting rule of thumb, NOT a single validated
    physical formula (rigorous phase determination needs a full
    vertical profile method, e.g. Bourgouin 2000's energy-area
    method, not implemented here).

    IMPORTANT LIMITATION: freezing rain and ice pellets (sleet) cannot
    be reliably told apart from surface temperature and wet-bulb
    temperature alone — both require a "warm nose" aloft (a melting
    layer above a sub-freezing surface layer); whether the particle
    re-freezes before reaching the ground (sleet) or stays liquid
    until impact (freezing rain) depends on the DEPTH and INTENSITY of
    that sub-freezing surface layer, which is profile information this
    surface-only classifier does not have. classify() below merges
    them into one category rather than picking an arbitrary,
    unverified surface threshold to separate two things it cannot
    actually distinguish.
    """

    @staticmethod
    def classify(surface_temperature_c: float, surface_wet_bulb_c: float) -> str:
        """
        Parameters
        ----------
        surface_temperature_c : float
            Surface air temperature (degC).
        surface_wet_bulb_c : float
            Surface wet-bulb temperature (degC) — see
            Thermodynamics.calculate_wet_bulb_temperature() /
            science/wet_bulb_temperature.py.

        Returns
        -------
        str
            "Rain" (Tw > 1.5 degC), "Freezing Rain / Ice Pellets"
            (ambiguous Tw zone, -0.5 to 1.5 degC, with a sub-freezing
            surface — see class docstring on why these two aren't
            split further), "Wet Snow/Mix" (ambiguous Tw zone with a
            surface temperature still above freezing), "Snow"
            (Tw <= -0.5 degC).
        """
        if surface_wet_bulb_c > 1.5:
            return "Rain"
        if surface_wet_bulb_c > -0.5:
            if surface_temperature_c <= 0.0:
                return "Freezing Rain / Ice Pellets"
            return "Wet Snow/Mix"
        return "Snow"
