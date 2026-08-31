"""
Atmospheric Complexity Framework (ACF)

Operational Wave Models & Spectral Wave Dynamics Module (Phase 2)
(WaveWatch III, WAM, SWAN, JONSWAP / Pierson-Moskowitz Spectra, Hs, Tp, Cg)
"""

import math
from dataclasses import dataclass


@dataclass
class WaveModelInfo:
    """Description scientifique d'un modèle numérique de vagues/houle."""

    key: str
    name: str
    institution: str
    equation_type: str  # e.g. "Spectral Action Balance Equation"
    spectral_resolution: str
    strengths: list[str]
    references: list[str]


WAVE_MODELS_REGISTRY: dict[str, WaveModelInfo] = {
    "wavewatch_3": WaveModelInfo(
        key="wavewatch_3",
        name="WAVEWATCH III (NOAA NCEP / US Navy)",
        institution="NOAA / NCEP / NASA",
        equation_type="Action Density Balance Equation dN/dt = S/sigma",
        spectral_resolution="24 directions x 32 frequencies (0.035 to 0.95 Hz)",
        strengths=["Référence mondiale pour les prévisions de houle globale et les tempêtes synoptiques"],
        references=["Tolman et al. (2014) NOAA Tech Note", "WAVEWATCH III Development Group (2019)"],
    ),
    "wam": WaveModelInfo(
        key="wam",
        name="WAM (Wave Model - ECMWF)",
        institution="ECMWF / WAMDI Group",
        equation_type="Energy Balance Equation dF/dt = S_in + S_nl + S_ds",
        spectral_resolution="36 directions x 36 frequencies",
        strengths=["Couplage bidirectionnel de surface avec le modèle atmosphérique IFS d'ECMWF"],
        references=["Komen et al. (1994) Cambridge University Press", "ECMWF Wave Model Doc"],
    ),
    "swan": WaveModelInfo(
        key="swan",
        name="SWAN (Simulating Waves Nearshore - TU Delft)",
        institution="Delft University of Technology (Netherlands)",
        equation_type="Nearshore Action Balance avec Déferlement Coastal",
        spectral_resolution="36 directions x 36 frequencies (0.04 to 1.0 Hz)",
        strengths=["Modélisation haute résolution du déferlement côtiere, shoaling et réfraction près des plages"],
        references=["Booij et al. (1999) J. Geophys. Res. 104, 7649-7666"],
    ),
}


class OperationalWaveEngine:
    """Moteur de calcul du spectre de vagues et des paramètres d'état de mer."""

    @staticmethod
    def significant_wave_height_from_spectrum(energy_m0: float) -> float:
        """Calcul de la hauteur significative des vagues Hs = 4 * sqrt(m0)."""
        return 4.0 * math.sqrt(max(0.0, energy_m0))

    @staticmethod
    def wave_group_velocity(peak_period_s: float, water_depth_m: float = 1000.0) -> float:
        """Calcul de la vitesse de groupe des vagues Cg en eau profonde Cg = g * T / (4 * pi)."""
        g = 9.80665
        return (g * peak_period_s) / (4.0 * math.pi)

    @classmethod
    def jonswap_spectrum_peak_energy(cls, wind_speed_10m: float, fetch_m: float) -> dict[str, float]:
        """Calcul du spectre de vagues JONSWAP selon le vent et le fetch."""
        g = 9.80665
        alpha = 0.076 * ((wind_speed_10m**2) / (fetch_m * g)) ** 0.22
        fp = 3.5 * (g / wind_speed_10m) * ((g * fetch_m) / (wind_speed_10m**2)) ** (-0.33)
        tp = 1.0 / fp if fp > 0 else 10.0
        hs = 0.0016 * math.sqrt(fetch_m) * wind_speed_10m

        return {
            "alpha_jonswap": alpha,
            "peak_frequency_hz": fp,
            "peak_period_s": tp,
            "significant_wave_height_m": hs,
        }
