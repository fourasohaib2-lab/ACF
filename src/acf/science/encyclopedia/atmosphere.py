"""
Atmospheric Physics Encyclopedia Domain
"""

import math

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

ENTRIES = [
    EncyclopediaEntry(
        key="ideal_gas_law",
        name="Équation d'État du Gaz Parfait",
        domain="Physique Atmosphérique",
        subdomain="Thermodynamique fondamentale",
        equation="p = rho * Rd * T",
        latex_equation=r"p = \rho R_d T",
        variables={
            "p": "Pression (Pa)",
            "rho": "Masse volumique (kg/m³)",
            "Rd": "287.058 J/(kg·K)",
            "T": "Température (K)",
        },
        units={"p": "Pa", "rho": "kg/m³", "T": "K"},
        description="Relation fondamentale d'état reliant la pression, la masse volumique et la température de l'air sec.",
        application_conditions=["Pression atmosphérique standard", "Gaz parfait en équilibre"],
        limitations=["Déviations légères aux très fortes pressions"],
        references=["WMO-No. 8", "NOAA Technical Report NWS 28"],
        compute_func=lambda density, temperature, Rd=287.058: density * Rd * temperature,
    ),
    EncyclopediaEntry(
        key="hydrostatic_equilibrium",
        name="Équilibre Hydrostatique",
        domain="Physique Atmosphérique",
        subdomain="Statique de l'atmosphère",
        equation="dp/dz = -rho * g",
        latex_equation=r"\frac{\partial p}{\partial z} = -\rho g",
        variables={"p": "Pression", "z": "Altitude", "rho": "Densité", "g": "Pesanteur"},
        units={"p": "Pa", "z": "m", "rho": "kg/m³", "g": "m/s²"},
        description="Équilibre vertical entre la force du gradient de pression et la force de pesanteur.",
        application_conditions=["Échelle synoptique et grande échelle"],
        limitations=["Absence d'accélération verticale rapide (non hydrostatique)"],
        references=["Holton & Hakim (2012)", "ECMWF IFS Documentation"],
        compute_func=lambda density, gravity=9.81, dz=1.0: -density * gravity * dz,
    ),
    EncyclopediaEntry(
        key="hypsometric_equation",
        name="Équation Hypsométrique",
        domain="Physique Atmosphérique",
        subdomain="Statique de l'atmosphère",
        equation="h2 - h1 = (Rd * Tv_bar / g) * ln(p1 / p2)",
        latex_equation=r"z_2 - z_1 = \frac{R_d \bar{T}_v}{g} \ln\left(\frac{p_1}{p_2}\right)",
        variables={
            "h1, h2": "Epaisseur de la couche (m)",
            "p1, p2": "Pressions aux limites (Pa)",
            "Tv_bar": "Température virtuelle moyenne",
        },
        units={"h": "m", "p": "Pa", "Tv_bar": "K"},
        description="Relie l'épaisseur géopotentielle d'une couche atmosphérique entre deux niveaux de pression à la température virtuelle moyenne.",
        application_conditions=["Atmosphère en équilibre hydrostatique"],
        limitations=["Variation spatiale de Tv supposée représentative par la moyenne"],
        references=["WMO Technical Note", "Holton & Hakim (2012)"],
        compute_func=lambda p1, p2, tv_bar, Rd=287.058, g=9.81: (Rd * tv_bar / g) * math.log(p1 / p2),
    ),
    EncyclopediaEntry(
        # NOTE (correction - registry key collision): renamed from
        # "boussinesq_approximation" (also used, independently, by
        # dynamics.py's density-perturbation-form entry) so both
        # formulations are independently accessible instead of one
        # silently shadowing the other depending on import order. See
        # EncyclopediaRegistry.register()'s collision guard.
        key="boussinesq_approximation_momentum_form",
        name="Approximation de Boussinesq",
        domain="Physique Atmosphérique",
        equation="d(rho)/dt ~ 0 except in buoyancy force g*(rho_prime/rho0)",
        latex_equation=r"\frac{D\mathbf{u}}{Dt} = -\frac{1}{\rho_0}\nabla p^\prime + B\mathbf{k} + \nu \nabla^2\mathbf{u}",
        variables={"rho_prime": "Perturbation de densité", "rho0": "Densité moyenne de référence", "B": "Flottabilité"},
        units={"B": "m/s²"},
        description="Néglige la variation de densité sauf dans le terme de poussée d'Archimède (flottabilité).",
        application_conditions=["Écoulements atmosphériques à faible profondeur convective"],
        limitations=["Non valable pour les couches atmosphériques très profondes (> 10 km)"],
        references=["Boussinesq (1903)", "Kundu & Cohen (2008) Fluid Mechanics"],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
