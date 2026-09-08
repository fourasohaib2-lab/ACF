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
        """
        Calcul de la vitesse de groupe des vagues Cg par la théorie linéaire (Airy) :
        Cg = n * C, avec C = omega / k et n = 0.5 * (1 + 2kh / sinh(2kh)),
        où le nombre d'onde k est résolu depuis la relation de dispersion
        omega^2 = g * k * tanh(k * h) (Newton-Raphson depuis l'approximation eau
        profonde k0 = omega^2 / g comme point de départ).

        NOTE (correction): water_depth_m was accepted but never used in the
        formula - this always returned the deep-water-only group velocity
        Cg = g*T/(4*pi) regardless of the depth argument (flagged by ruff
        ARG004, the same "unused physical parameter" pattern already swept
        elsewhere in this codebase). Deep water remains the correct limit
        here (n -> 0.5, tanh(kh) -> 1 recovers the exact old formula), but a
        shallow depth now genuinely changes the result via the real
        dispersion relation instead of being silently ignored.
        """
        g = 9.80665
        omega = 2.0 * math.pi / peak_period_s
        k = (omega**2) / g  # deep-water wavenumber as the Newton-Raphson initial guess
        for _ in range(50):
            th = math.tanh(k * water_depth_m)
            f = g * k * th - omega**2
            df = g * th + g * k * water_depth_m * (1.0 - th**2)
            if df == 0.0:
                break
            k_next = k - f / df
            if k_next <= 0.0:
                k_next = k / 2.0
            if abs(k_next - k) < 1e-12:
                k = k_next
                break
            k = k_next

        c = omega / k
        kh = k * water_depth_m
        # sinh(2kh) overflows for kh >> 1; the deep-water limit (n=0.5) applies well before that.
        n = 0.5 * (1.0 + (2.0 * kh) / math.sinh(2.0 * kh)) if kh < 350.0 else 0.5
        return n * c

    @classmethod
    def jonswap_spectrum_peak_energy(cls, wind_speed_10m: float, fetch_m: float) -> dict[str, float]:
        """
        Calcul du spectre de vagues JONSWAP selon le vent et le fetch.

        NOTE (correction — dimensionally wrong formula): the fetch-limited
        significant wave height formula was "0.0016 * sqrt(fetch_m) *
        wind_speed_10m", missing a division by sqrt(g). That expression's
        units are m^1.5/s, not meters - not a valid wave height at all,
        and numerically ~3.13x (sqrt(g)) too large. The standard
        dimensionless fetch-limited relation (Hasselmann et al. 1973,
        JONSWAP; see also CEM 2002) is
        g*Hs/U10^2 = 0.0016 * sqrt(g*fetch/U10^2), which solves to
        Hs = 0.0016 * U10 * sqrt(fetch/g) - the missing sqrt(g) restored
        below. E.g. at U10=15 m/s, fetch=100 km this was giving Hs~7.6 m
        instead of the physically correct ~2.4 m.
        """
        g = 9.80665
        alpha = 0.076 * ((wind_speed_10m**2) / (fetch_m * g)) ** 0.22
        fp = 3.5 * (g / wind_speed_10m) * ((g * fetch_m) / (wind_speed_10m**2)) ** (-0.33)
        tp = 1.0 / fp if fp > 0 else 10.0
        hs = 0.0016 * wind_speed_10m * math.sqrt(fetch_m / g)

        return {
            "alpha_jonswap": alpha,
            "peak_frequency_hz": fp,
            "peak_period_s": tp,
            "significant_wave_height_m": hs,
        }
