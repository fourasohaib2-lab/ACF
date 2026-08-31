"""
Aerodynamics & Flight Mechanics Atmospheric Encyclopedia Module
"""

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

ENTRIES = [
    EncyclopediaEntry(
        key="aerodynamic_lift_force",
        name="Équation de la Force de Portance Aérodynamique",
        domain="Aéronautique",
        subdomain="Aérodynamique",
        equation="L = 0.5 * rho * V^2 * S * Cz",
        latex_equation=r"L = \frac{1}{2} \rho V^2 S C_z",
        variables={
            "rho": "Masse volumique de l'air (kg/m³)",
            "V": "Vitesse vraie VTA (m/s)",
            "S": "Surface alaire (m²)",
            "Cz": "Coefficient de portance",
        },
        units={"L": "N", "V": "m/s"},
        description="Force perpendiculaire au vent relatif engendrée par la différence de pression entre l'intrados et l'extrados de l'aile (théorème de Bernoulli et circulation de Kutta-Joukowski).",
        application_conditions=["Écoulement autour d'un profil d'aile non décroché"],
        limitations=["Décrochage aérodynamique aux grands angles d'incidence (> 15°)"],
        references=["ICAO Aerodynamics Manual", "Anderson (2017) Fundamentals of Aerodynamics"],
        compute_func=lambda density, velocity, surface_area, Cz: 0.5 * density * (velocity**2) * surface_area * Cz,
    ),
    EncyclopediaEntry(
        key="bernoulli_principle_flow",
        name="Théorème de Bernoulli pour Fluide Incompressible",
        domain="Aéronautique",
        subdomain="Mécanique des fluides",
        equation="p + 0.5 * rho * V^2 + rho * g * z = Constant",
        latex_equation=r"p + \frac{1}{2}\rho V^2 + \rho g z = \text{Cte}",
        variables={"p": "Pression statique (Pa)", "0.5*rho*V^2": "Pression dynamique (Pa)"},
        units={"p": "Pa"},
        description="Conservation de l'énergie mécanique totale le long d'une ligne de courant fluide.",
        application_conditions=["Fluide parfait, incompressible et écoulement stationnaire"],
        limitations=["Invalide pour les écoulements supersoniques (effets de compressibilité)"],
        references=["Bernoulli (1738) Hydrodynamica", "Anderson (2017)"],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
