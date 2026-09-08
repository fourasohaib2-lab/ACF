"""
Atmospheric Complexity Framework (ACF)

Orbital Mechanics Engine Module (Phase 2)
(OrbitalMechanicsEngine implementing Kepler's Laws, Vis-Viva equation, Kepler Equation, Lagrange points L1-L5)
"""

import math

# Constants (SI units)
G_CONST = 6.67430e-11  # m^3 kg^-1 s^-2
MASS_SUN = 1.98847e30  # kg
MASS_EARTH = 5.9722e24  # kg
AU_METERS = 1.495978707e11  # meters


class OrbitalMechanicsEngine:
    """
    Moteur de mécanique céleste et orbitale (Lois de Kepler, équation Vis-Viva, résolution de Kepler).
    """

    @classmethod
    def vis_viva_velocity(cls, r_m: float, a_m: float, central_mass_kg: float = MASS_SUN) -> float:
        """
        Calcule la vitesse orbitale par l'équation Vis-Viva : v = sqrt(G * M * (2/r - 1/a))

        Equations:
            v = \\sqrt{G \\cdot M \\left(\\frac{2}{r} - \\frac{1}{a}\\right)}
        """
        mu = G_CONST * central_mass_kg
        if a_m <= 0:  # Parabolique / Hyperbolique
            return math.sqrt(2.0 * mu / r_m)
        return math.sqrt(mu * (2.0 / r_m - 1.0 / a_m))

    @classmethod
    def orbital_period(cls, a_m: float, central_mass_kg: float = MASS_SUN) -> float:
        """
        Calcule la période orbitale par la 3ème loi de Kepler : T = 2*pi * sqrt(a^3 / (G*M))

        Equations:
            T = 2\\pi \\sqrt{\\frac{a^3}{G \\cdot M}}
        """
        mu = G_CONST * central_mass_kg
        return 2.0 * math.pi * math.sqrt((a_m**3) / mu)

    @classmethod
    def solve_kepler_equation(cls, M_rad: float, e: float, max_iter: int = 100, tol: float = 1e-10) -> float:
        """
        Résout l'équation de Kepler M = E - e*sin(E) par la méthode de Newton-Raphson.

        Equations:
            f(E) = E - e \\sin E - M = 0
            E_{n+1} = E_n - \\frac{E_n - e \\sin E_n - M}{1 - e \\cos E_n}
        """
        E = M_rad
        for _ in range(max_iter):
            f = E - e * math.sin(E) - M_rad
            f_prime = 1.0 - e * math.cos(E)
            delta = f / f_prime
            E -= delta
            if abs(delta) < tol:
                break
        return E

    @classmethod
    def perihelion_aphelion_distances(cls, a_m: float, e: float) -> dict[str, float]:
        """Calcule la distance au périhélie q = a(1-e) et à l'aphélie Q = a(1+e)."""
        return {
            "perihelion_m": a_m * (1.0 - e),
            "aphelion_m": a_m * (1.0 + e),
            "perihelion_au": (a_m * (1.0 - e)) / AU_METERS,
            "aphelion_au": (a_m * (1.0 + e)) / AU_METERS,
        }

    @classmethod
    def lagrange_l1_distance(cls, r_orbit_m: float, m1_kg: float = MASS_SUN, m2_kg: float = MASS_EARTH) -> float:
        """
        Calcule la distance approximative du point de Lagrange L1 : r_L1 = R * (m2 / (3*m1))^(1/3)

        Equations:
            r_{L1} = R \\left(\\frac{m_2}{3 m_1}\\right)^{1/3}
        """
        return r_orbit_m * ((m2_kg / (3.0 * m1_kg)) ** (1.0 / 3.0))
