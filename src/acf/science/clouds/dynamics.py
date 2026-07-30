"""
Atmospheric Complexity Framework (ACF)

Cloud Dynamics Engine
"""

import math
from acf.science.clouds.base import CloudProcess
from acf.science.clouds.registry import CloudScientificRegistry


class CloudDynamicsEngine:
    """
    Moteur de dynamique nuageuse (ascendance/subsidence, entraînement, flux de masse, Navier-Stokes).
    """

    def __init__(self):
        self._register_dynamics_processes()

    def _register_dynamics_processes(self):
        processes = [
            CloudProcess(
                key="convective_mass_flux",
                name="Flux de Masse Convectif",
                domain="Dynamique Nuageuse",
                equation="M = rho * w * sigma",
                variables={"rho": "Masse volumique (kg/m³)", "w": "Vitesse d'ascendance (m/s)", "sigma": "Fraction surfacique couverte [0, 1]"},
                units={"M": "kg/(m²·s)"},
                description="Flux de masse vertical ascendant transporté par les cellules convectives.",
                references=["Tiedtke (1989) Mon. Wea. Rev.", "ECMWF Convection Documentation"],
                compute_func=self.mass_flux,
            ),
            CloudProcess(
                key="updraft_velocity_buoyancy",
                name="Vitesse Max d'Ascendance (CAPE)",
                domain="Dynamique Nuageuse",
                equation="w_max = sqrt(2 * CAPE)",
                variables={"CAPE": "Énergie convective (J/kg)"},
                units={"w_max": "m/s"},
                description="Vitesse maximale théorique du courant ascendant au sommet du nuage en l'absence d'entraînement.",
                references=["Holton & Hakim (2012)"],
                compute_func=self.max_updraft_velocity,
            ),
            CloudProcess(
                key="entrainment_rate",
                name="Taux d'Entraînement de l'Air Environnant",
                domain="Dynamique Nuageuse",
                equation="dM/dz = epsilon * M - delta * M",
                variables={"epsilon": "Taux d'entraînement (m⁻¹)", "delta": "Taux de détraitement (m⁻¹)"},
                units={"dM/dz": "kg/(m³·s)"},
                description="Infiltration d'air sec environnemental diluant la parcelle convective en ascendance.",
                references=["Morton, Taylor & Turner (1956)", "Tiedtke (1989)"],
                compute_func=self.entrainment_detrainment,
            ),
        ]
        for p in processes:
            CloudScientificRegistry.register(p)

    def mass_flux(self, density: float, updraft_w: float, area_fraction: float = 0.05) -> float:
        """Calcule M = rho * w * sigma."""
        return density * max(updraft_w, 0.0) * max(min(area_fraction, 1.0), 0.0)

    def max_updraft_velocity(self, cape: float) -> float:
        """Calcule w_max = sqrt(2 * CAPE)."""
        if cape <= 0:
            return 0.0
        return math.sqrt(2.0 * cape)

    def entrainment_detrainment(self, mass_flux: float, entrainment_rate: float = 1e-4, detrainment_rate: float = 1e-4, dz: float = 100.0) -> float:
        """Calcule la variation du flux de masse avec l'altitude dM/dz * dz."""
        return (entrainment_rate - detrainment_rate) * mass_flux * dz

    def cloud_top_evolution(self, current_top_z: float, updraft_w: float, dt: float = 60.0) -> float:
        """Évolution temporelle du sommet du nuage."""
        return current_top_z + updraft_w * dt

    def navier_stokes_vertical(self, density: float, buoyancy_force: float, drag_force: float = 0.0) -> float:
        """Accélération verticale dw/dt = buoyancy - drag."""
        return buoyancy_force - drag_force
