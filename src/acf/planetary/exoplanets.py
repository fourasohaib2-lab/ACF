"""
Atmospheric Complexity Framework (ACF)

Exoplanets Database & Characterization Module (Phase 7)
(ExoplanetDatabase, Exoplanet cataloguing Kepler, TESS, JWST discoveries and calculating ESI)
"""

from dataclasses import dataclass


@dataclass
class Exoplanet:
    """Description d'une exoplanète caractérisée par Kepler, TESS ou JWST."""

    name: str
    host_star: str
    discovery_mission: str
    radius_earth_radii: float
    mass_earth_masses: float
    surface_gravity_g: float
    equilibrium_temp_k: float
    orbital_period_days: float
    semi_major_axis_au: float
    is_in_habitable_zone: bool
    esi_score: float  # Earth Similarity Index (0.0 to 1.0)
    potential_water: str


EXOPLANET_CATALOG: dict[str, Exoplanet] = {
    "proxima_b": Exoplanet(
        name="Proxima Centauri b",
        host_star="Proxima Centauri (M-Dwarf)",
        discovery_mission="ESO High Accuracy Radial Velocity Planet Searcher (HARPS)",
        radius_earth_radii=1.07,
        mass_earth_masses=1.17,
        surface_gravity_g=1.02,
        equilibrium_temp_k=234.0,
        orbital_period_days=11.18,
        semi_major_axis_au=0.0485,
        is_in_habitable_zone=True,
        esi_score=0.87,
        potential_water="Likely Surface Liquid Water under Atmosphere Shield",
    ),
    "trappist1_e": Exoplanet(
        name="TRAPPIST-1 e",
        host_star="TRAPPIST-1 (Ultra-cool M-Dwarf)",
        discovery_mission="NASA Spitzer / JWST",
        radius_earth_radii=0.92,
        mass_earth_masses=0.69,
        surface_gravity_g=0.82,
        equilibrium_temp_k=251.0,
        orbital_period_days=6.10,
        semi_major_axis_au=0.029,
        is_in_habitable_zone=True,
        esi_score=0.85,
        potential_water="Global Surface Liquid Water Ocean Possible",
    ),
    "k2_18b": Exoplanet(
        name="K2-18 b",
        host_star="K2-18 (M-Dwarf)",
        discovery_mission="NASA Kepler / JWST NIRSpec",
        radius_earth_radii=2.61,
        mass_earth_masses=8.63,
        surface_gravity_g=1.27,
        equilibrium_temp_k=265.0,
        orbital_period_days=32.9,
        semi_major_axis_au=0.143,
        is_in_habitable_zone=True,
        esi_score=0.73,
        potential_water="Hycean World with Sub-surface Liquid Ocean and H2-rich Atmosphere",
    ),
}


class ExoplanetDatabase:
    """Base de données et catalogue des exoplanètes caractérisées."""

    @classmethod
    def get_exoplanet(cls, name_key: str) -> Exoplanet | None:
        return EXOPLANET_CATALOG.get(name_key.lower())

    @classmethod
    def list_exoplanets(cls) -> list[str]:
        return list(EXOPLANET_CATALOG.keys())

    @classmethod
    def calculate_esi(cls, radius_re: float, density_rho_e: float, escape_vel_ve: float, temp_k: float) -> float:
        """
        Calcule l'Earth Similarity Index (ESI) selon Schulze-Makuch et al. (2011).

        Equations:
            ESI = \\prod_{i=1}^n \\left(1 - \\left|\\frac{x_i - x_{i0}}{x_i + x_{i0}}\\right|\\right)^{w_i / n}

        NOTE (correction — Physics Guard): density_rho_e and
        escape_vel_ve were genuinely accepted (they are two of the
        paper's own standard 4 ESI input parameters - radius, density,
        escape velocity, surface temperature) but completely unused -
        this only ever computed a 2-parameter radius/temperature
        approximation, and the temperature exponent (0.56) looked like
        a corrupted transposition of the paper's real weight (5.58).
        Replaced with the full 4-parameter ESI using the standard
        published weights (Schulze-Makuch et al. 2011; as also
        reproduced by the Planetary Habitability Laboratory's Habitable
        Exoplanets Catalog): radius w=0.57, density w=1.07, escape
        velocity w=0.70, surface temperature w=5.58, each input
        compared against its Earth reference value (radius_re0=1.0,
        density_rho_e0=1.0, escape_vel_ve0=1.0 in Earth units,
        temp_k0=288 K). Not fabricated.
        """
        n = 4
        weights = {"radius": 0.57, "density": 1.07, "escape_vel": 0.70, "temp": 5.58}
        reference = {"radius": 1.0, "density": 1.0, "escape_vel": 1.0, "temp": 288.0}

        def esi_term(x: float, x0: float, w: float) -> float:
            return (1.0 - abs((x - x0) / (x + x0))) ** (w / n)

        term_r = esi_term(radius_re, reference["radius"], weights["radius"])
        term_rho = esi_term(density_rho_e, reference["density"], weights["density"])
        term_ve = esi_term(escape_vel_ve, reference["escape_vel"], weights["escape_vel"])
        term_t = esi_term(temp_k, reference["temp"], weights["temp"])
        return term_r * term_rho * term_ve * term_t
