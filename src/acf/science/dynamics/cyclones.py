"""
Cyclones
========

Gradient wind, baroclinic Rossby radius of deformation, Brunt-Väisälä
frequency, bombogenesis (explosive cyclogenesis), and the Saffir-Simpson
hurricane wind scale.

Reference:
    Sanders, F., & Gyakum, J. R. (1980). "Synoptic-Dynamic Climatology
    of the 'Bomb'". Mon. Wea. Rev., 108(10), 1589-1606.
    Holton, J. R., & Hakim, G. J. (2012). "An Introduction to Dynamic
    Meteorology" (5th ed.).
    NOAA National Hurricane Center — Saffir-Simpson Hurricane Wind
    Scale.
"""

import math

from acf.science.constants import G

BOMB_REFERENCE_LATITUDE_DEG = 60.0


class GradientWind:
    """Gradient wind balance for curved flow (cyclonic/anticyclonic)."""

    @staticmethod
    def calculate(
        radius_m: float,
        coriolis_f: float,
        density: float,
        radial_pressure_gradient_pa_m: float,
        cyclonic: bool = True,
    ) -> float:
        """
        Solves the gradient wind quadratic V^2/R + f*V - (1/rho)*dp/dr = 0
        for the physically valid root.

            V = -f*R/2 +/- sqrt((f*R/2)^2 + R/rho * dp/dr)

        The '+' root (cyclonic, low pressure center, radial_pressure_
        gradient_pa_m > 0 outward) gives the physically valid subgeo-
        strophic solution; the '-' root corresponds to anticyclonic
        (high pressure center) flow.

        Parameters
        ----------
        radius_m : float
            Radius of curvature (m), > 0.
        coriolis_f : float
            Coriolis parameter (s^-1), non-zero.
        density : float
            Air density (kg/m^3), > 0.
        radial_pressure_gradient_pa_m : float
            dp/dr, radial pressure gradient (Pa/m). Positive for a
            cyclone (pressure increases outward from the low center).
        cyclonic : bool
            True for the cyclonic (low-pressure) root, False for the
            anticyclonic (high-pressure) root.

        Returns
        -------
        float
            Gradient wind speed (m/s).

        Raises
        ------
        ValueError
            If radius_m/density are non-positive, coriolis_f is zero,
            or the discriminant is negative (no real solution — the
            anticyclonic case has an upper bound on the pressure
            gradient beyond which gradient balance is impossible).

        Reference
        ---------
        Holton & Hakim (2012), Ch. 3.
        """
        if radius_m <= 0:
            raise ValueError("radius_m must be positive.")
        if density <= 0:
            raise ValueError("density must be positive.")
        if coriolis_f == 0:
            raise ValueError("coriolis_f must not be zero.")

        half_fr = coriolis_f * radius_m / 2.0
        discriminant = half_fr**2 + (radius_m / density) * radial_pressure_gradient_pa_m

        if discriminant < 0:
            raise ValueError("no real gradient-wind solution for these inputs (discriminant < 0).")

        sqrt_term = math.sqrt(discriminant)
        if cyclonic:
            return -half_fr + sqrt_term
        return -half_fr - sqrt_term


class BruntVaisalaFrequency:
    """Static stability frequency N."""

    @staticmethod
    def calculate(potential_temperature_k: float, dtheta_dz: float) -> float:
        """
        N^2 = (g/theta) * (dtheta/dz)

        Parameters
        ----------
        potential_temperature_k : float
            Reference potential temperature (K), > 0.
        dtheta_dz : float
            Vertical gradient of potential temperature (K/m).

        Returns
        -------
        float
            N (rad/s). Returns 0 if dtheta_dz <= 0 (statically neutral
            or unstable — N^2 would be <= 0, N is only physically
            meaningful, as an oscillation frequency, when stable).

        Reference
        ---------
        Holton & Hakim (2012), Ch. 2.
        """
        if potential_temperature_k <= 0:
            raise ValueError("potential_temperature_k must be positive.")
        n_squared = (G / potential_temperature_k) * dtheta_dz
        if n_squared <= 0:
            return 0.0
        return math.sqrt(n_squared)


class RossbyRadius:
    """Baroclinic (internal) Rossby radius of deformation."""

    @staticmethod
    def baroclinic(brunt_vaisala_n: float, scale_height_m: float, coriolis_f: float) -> float:
        """
        L_R = N * H / f

        Parameters
        ----------
        brunt_vaisala_n : float
            Brunt-Väisälä frequency (rad/s), > 0.
        scale_height_m : float
            Characteristic vertical length scale (m), e.g. tropopause
            height, > 0.
        coriolis_f : float
            Coriolis parameter (s^-1), non-zero.

        Returns
        -------
        float
            Baroclinic Rossby radius of deformation (m).

        Reference
        ---------
        Holton & Hakim (2012), Ch. 6.
        """
        if brunt_vaisala_n <= 0:
            raise ValueError("brunt_vaisala_n must be positive.")
        if scale_height_m <= 0:
            raise ValueError("scale_height_m must be positive.")
        if coriolis_f == 0:
            raise ValueError("coriolis_f must not be zero.")
        return brunt_vaisala_n * scale_height_m / abs(coriolis_f)


class Bombogenesis:
    """Explosive cyclogenesis ('bomb') diagnosis, Sanders & Gyakum (1980)."""

    @staticmethod
    def threshold_hpa_24h(latitude_deg: float) -> float:
        """
        Latitude-normalized 24h pressure-drop threshold for a 'bomb':

            threshold(phi) = 24 * sin(phi) / sin(60 deg)

        Parameters
        ----------
        latitude_deg : float
            Latitude (degrees), must satisfy 0 < |latitude| <= 90
            (undefined/zero at the equator).

        Returns
        -------
        float
            Threshold (hPa/24h). E.g. ~28 hPa at the poles, ~12 hPa
            at 25 deg latitude — matches Sanders & Gyakum's own
            published examples.

        Reference
        ---------
        Sanders & Gyakum (1980), Mon. Wea. Rev., 108(10), 1589-1606.
        """
        if not (-90.0 <= latitude_deg <= 90.0):
            raise ValueError("latitude_deg must be in [-90, 90].")
        if latitude_deg == 0:
            raise ValueError("threshold is undefined at the equator (sin(0)=0).")

        return 24.0 * math.sin(math.radians(abs(latitude_deg))) / math.sin(math.radians(BOMB_REFERENCE_LATITUDE_DEG))

    @staticmethod
    def bergeron_units(pressure_drop_24h_hpa: float, latitude_deg: float) -> float:
        """
        Bergeron units = actual 24h pressure drop / latitude-normalized
        threshold. >= 1.0 means the cyclone qualifies as a 'bomb'
        (explosive cyclogenesis).

        Parameters
        ----------
        pressure_drop_24h_hpa : float
            Observed central pressure drop over 24h (hPa), >= 0.
        latitude_deg : float
            Latitude (degrees).

        Returns
        -------
        float
            Bergeron units (dimensionless).
        """
        if pressure_drop_24h_hpa < 0:
            raise ValueError("pressure_drop_24h_hpa must be non-negative.")
        threshold = Bombogenesis.threshold_hpa_24h(latitude_deg)
        return pressure_drop_24h_hpa / threshold

    @staticmethod
    def is_bomb(pressure_drop_24h_hpa: float, latitude_deg: float) -> bool:
        """True if the cyclone meets or exceeds 1 Bergeron unit."""
        return Bombogenesis.bergeron_units(pressure_drop_24h_hpa, latitude_deg) >= 1.0


class SaffirSimpson:
    """Saffir-Simpson Hurricane Wind Scale (NOAA National Hurricane Center)."""

    @staticmethod
    def category(max_sustained_wind_kt: float) -> str:
        """
        Classify 1-minute maximum sustained wind speed into the
        Saffir-Simpson scale.

        Parameters
        ----------
        max_sustained_wind_kt : float
            Maximum sustained (1-minute) wind speed (knots), >= 0.

        Returns
        -------
        str
            "Tropical Depression" (<34kt), "Tropical Storm" (34-63kt),
            "Category 1" (64-82kt), "Category 2" (83-95kt),
            "Category 3" (96-112kt), "Category 4" (113-136kt),
            "Category 5" (>=137kt).

        Reference
        ---------
        NOAA National Hurricane Center, Saffir-Simpson Hurricane Wind
        Scale.
        """
        if max_sustained_wind_kt < 0:
            raise ValueError("max_sustained_wind_kt must be non-negative.")

        w = max_sustained_wind_kt
        if w < 34:
            return "Tropical Depression"
        if w < 64:
            return "Tropical Storm"
        if w < 83:
            return "Category 1"
        if w < 96:
            return "Category 2"
        if w < 113:
            return "Category 3"
        if w < 137:
            return "Category 4"
        return "Category 5"

    @staticmethod
    def is_major_hurricane(max_sustained_wind_kt: float) -> bool:
        """Category 3 or higher (>= 96kt) is classified as a 'major hurricane'."""
        return max_sustained_wind_kt >= 96
