"""
Atmospheric Complexity Framework (ACF)

Global Seismology, Earthquake Laws & Moment Tensor Module (Phase 4)
(Moment Magnitude Mw, Gutenberg-Richter Law, Omori Aftershock Law, Bath's Law, PGA, PGV, MMI)
"""

import math
from dataclasses import dataclass


@dataclass
class MomentTensor:
    """Composantes du tenseur du moment sismique M = [[Mxx, Mxy, Mxz], [Myx, Myy, Myz], [Mzx, Mzy, Mzz]] (N.m)."""

    mrr: float
    mtt: float
    mpp: float
    mrt: float
    mrp: float
    mtp: float

    @property
    def scalar_seismic_moment_m0(self) -> float:
        """Calcul du moment sismique scalaire M0 = sqrt(0.5 * sum(M_ij²))."""
        val = self.mrr**2 + self.mtt**2 + self.mpp**2 + 2 * (self.mrt**2 + self.mrp**2 + self.mtp**2)
        return math.sqrt(0.5 * val)


@dataclass
class EarthquakeEvent:
    """Description complète d'un événement séisme."""

    event_id: str
    latitude: float
    longitude: float
    depth_km: float
    magnitude_mw: float
    seismic_moment_m0_nm: float
    epicenter_name: str
    origin_time_utc: str
    pga_g: float  # Peak Ground Acceleration (in g)
    pgv_cm_s: float  # Peak Ground Velocity (cm/s)
    mmi_intensity: str  # Modified Mercalli Intensity (I - XII)


class SeismologyEngine:
    """Moteur des équations sismologiques fondamentales."""

    @staticmethod
    def moment_magnitude_mw(seismic_moment_m0_nm: float) -> float:
        """Calcul de la magnitude de moment Mw = (2/3) * log10(M0) - 6.07 (avec M0 en N.m)."""
        if seismic_moment_m0_nm <= 0:
            return 0.0
        return (2.0 / 3.0) * math.log10(seismic_moment_m0_nm) - 6.07

    @staticmethod
    def seismic_moment_m0(shear_modulus_pa: float, area_m2: float, average_slip_m: float) -> float:
        """Calcul du moment sismique M0 = mu * A * D (N.m)."""
        return shear_modulus_pa * area_m2 * average_slip_m

    @staticmethod
    def gutenberg_richter_frequency(a_value: float, b_value: float, min_magnitude: float) -> float:
        """Loi de Gutenberg-Richter : log10(N) = a - b * M => N = 10^(a - b*M)."""
        return 10.0 ** (a_value - b_value * min_magnitude)

    @staticmethod
    def omori_aftershock_rate(
        time_days: float, k_const: float = 100.0, c_const: float = 0.1, p_exponent: float = 1.0
    ) -> float:
        """Loi d'Omori modifiée pour le taux de répliques n(t) = K / (t + c)^p."""
        return k_const / ((time_days + c_const) ** p_exponent)

    @staticmethod
    def bath_law_largest_aftershock(mainshock_mw: float) -> float:
        """Loi de Bath : La plus grande réplique a une magnitude d'environ M_main - 1.2."""
        return max(0.0, mainshock_mw - 1.2)


class EarthquakeDatabase:
    """Base de données et registre des séismes majeurs mondiaux."""

    @classmethod
    def get_sample_earthquake(cls, event_id: str = "US2011TOHOKU") -> EarthquakeEvent:
        """Génère une fiche de séisme majeur (ex: Tohoku 2011 Mw 9.1)."""
        return EarthquakeEvent(
            event_id=event_id,
            latitude=38.297,
            longitude=142.373,
            depth_km=29.0,
            magnitude_mw=9.1,
            seismic_moment_m0_nm=5.3e22,
            epicenter_name="Off the Pacific Coast of Tohoku, Japan",
            origin_time_utc="2011-03-11T05:46:24Z",
            pga_g=2.7,
            pgv_cm_s=110.0,
            mmi_intensity="IX (Violent)",
        )
