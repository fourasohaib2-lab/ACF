"""
Atmospheric Complexity Framework (ACF)

Cosmic Impact Physics Engine Module (Phase 3)
(ImpactEngine, ImpactSeverity calculating impact kinetic energy E = 0.5*m*v^2, crater diameter, shockwaves, airbursts)
"""

from dataclasses import dataclass


JOULES_PER_MEGATON_TNT = 4.184e15  # Joules per Mt TNT
GRAVITY_EARTH = 9.80665  # m/s^2


@dataclass
class ImpactSeverity:
    """Description physique de la sévérité d'un impact cosmique."""
    kinetic_energy_joules: float
    megatons_tnt: float
    crater_diameter_km: float
    overpressure_pascal_at_100km: float
    thermal_radiation_j_m2_at_100km: float
    is_global_extinction_event: bool
    severity_label: str


class ImpactEngine:
    """
    Moteur physique de simulation des impacts d'astéroïdes et comètes sur la Terre.
    """

    @classmethod
    def calculate_kinetic_energy(cls, mass_kg: float, velocity_m_s: float) -> float:
        """
        Calcule l'énergie cinétique d'impact : E = 0.5 * m * v^2
        
        Equations:
            E = \\frac{1}{2} m v^2
        """
        return 0.5 * mass_kg * (velocity_m_s**2)

    @classmethod
    def joules_to_megatons(cls, energy_joules: float) -> float:
        """Convertit l'énergie en Megatons de TNT."""
        return energy_joules / JOULES_PER_MEGATON_TNT

    @classmethod
    def estimate_crater_diameter_km(cls, diameter_m: float, velocity_m_s: float, density_impactor: float = 2500.0, density_target: float = 2700.0) -> float:
        """
        Estime le diamètre du cratère d'impact par la formule empirique d'échelle de Collins et al. (2005).
        
        Equations:
            D_{\\text{crater}} = 1.161 \\cdot \\left(\\frac{\\rho_i}{\\rho_t}\\right)^{0.33} \\cdot d_i^{0.78} \\cdot v_i^{0.44} \\cdot g^{-0.22}
        """
        d_km = 1.161 * ((density_impactor / density_target) ** (0.33)) * (diameter_m**0.78) * (velocity_m_s**0.44) * (GRAVITY_EARTH ** -0.22)
        return d_km / 1000.0

    @classmethod
    def simulate_impact(cls, diameter_m: float, velocity_km_s: float, mass_kg: float) -> ImpactSeverity:
        """Simule un impact cosmique et retourne un bilan physique complet."""
        v_m_s = velocity_km_s * 1000.0
        energy_j = cls.calculate_kinetic_energy(mass_kg, v_m_s)
        mt_tnt = cls.joules_to_megatons(energy_j)
        crater_km = cls.estimate_crater_diameter_km(diameter_m, v_m_s)

        overpressure = 1e5 * ((mt_tnt / 1.0) ** 0.33)  # Pascal à 100 km
        thermal = 1e4 * (mt_tnt / 1.0)  # J/m^2 à 100 km
        is_global = mt_tnt >= 1.0e6  # > 1 million megatons = extinction globale

        if mt_tnt < 1.0:
            label = "LOCAL AIRBURST / CHELYABINSK TYPE"
        elif mt_tnt < 1000.0:
            label = "REGIONAL DESTRUCTIVE IMPACT / TUNGUSKA TYPE"
        elif mt_tnt < 100000.0:
            label = "CONTINENTAL CATACLYSM"
        else:
            label = "GLOBAL EXTINCTION EVENT / CHICXULUB TYPE"

        return ImpactSeverity(
            kinetic_energy_joules=energy_j,
            megatons_tnt=mt_tnt,
            crater_diameter_km=crater_km,
            overpressure_pascal_at_100km=overpressure,
            thermal_radiation_j_m2_at_100km=thermal,
            is_global_extinction_event=is_global,
            severity_label=label,
        )
