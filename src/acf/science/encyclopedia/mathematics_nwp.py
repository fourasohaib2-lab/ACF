"""
Applied Mathematics for NWP Encyclopedia Module
"""

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

ENTRIES = [
    EncyclopediaEntry(
        key="spherical_harmonics_nwp",
        name="Harmoniques Sphériques (Base des Modèles Spectraux)",
        domain="Mathématiques NWP",
        subdomain="Méthodes spectrales",
        equation="Y_lm(lat, lon) = P_lm(sin(lat)) * exp(i * m * lon)",
        latex_equation=r"Y_l^m(\phi, \lambda) = P_l^m(\sin\phi) e^{i m \lambda}",
        variables={"Plm": "Polynômes associés de Legendre", "l": "Nombre d'onde total", "m": "Nombre d'onde zonal"},
        units={"Y": "dimensionless"},
        description="Fonctions propres de l'opérateur Laplacien sur la sphère servant de base orthogonale d'expansion dans ECMWF IFS et ARPEGE.",
        application_conditions=["Modèles atmosphériques sphériques spectraux"],
        limitations=["Calculs coûteux des transformées de Legendre à très haute résolution (TCo1279+)"],
        references=["Durran (2010) Numerical Methods for Fluid Dynamics", "ECMWF Spectral Docs"],
    ),
    EncyclopediaEntry(
        key="semi_lagrangian_advection",
        name="Schéma d'Advection Semi-Lagrangien",
        domain="Mathématiques NWP",
        subdomain="Intégration temporelle",
        equation="psi(x, t+dt) = psi(x - V*dt, t)",
        latex_equation=r"\psi(\mathbf{x}, t+\Delta t) = \psi(\mathbf{x} - \mathbf{V}\Delta t, t)",
        variables={"x": "Point de grille d'arrivée", "x - V*dt": "Point de départ de la trajectoire fluide (departure point)"},
        units={"psi": "champ transporté"},
        description="Méthode de transport inconditionnellement stable affranchie de la condition de Courant-Friedrichs-Lewy (CFL), permettant de grands pas de temps dt.",
        application_conditions=["Modèles NWP mondiaux et régionaux (ECMWF IFS, AROME)"],
        limitations=["Interpolation d'ordre élevé requise (spline ou lagrangienne 3D) pour limiter la diffusion numérique"],
        references=["Robert (1981) Atmos. Ocean", "Staniforth & Côté (1991) Mon. Wea. Rev."],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
