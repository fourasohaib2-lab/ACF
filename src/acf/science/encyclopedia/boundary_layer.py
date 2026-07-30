"""
Atmospheric Boundary Layer Encyclopedia Domain
"""

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

ENTRIES = [
    EncyclopediaEntry(
        key="turbulent_kinetic_energy",
        name="Énergie Cinétique Turbulente (TKE)",
        domain="Couche Limite Atmosphérique",
        equation="e = 0.5 * (u_prime^2 + v_prime^2 + w_prime^2)",
        latex_equation=r"e = \frac{1}{2}\left(\overline{u^{\prime 2}} + \overline{v^{\prime 2}} + \overline{w^{\prime 2}}\right)",
        variables={"u_prime, v_prime, w_prime": "Fluctuations turbulentes des 3 composantes du vent"},
        units={"e": "m²/s²"},
        description="Mesure de l'intensité moyenne des rumeurs et tourbillons turbulents dans la couche limite.",
        application_conditions=["Couche limite atmosphérique agitée"],
        limitations=["Décomposition de Reynolds requise"],
        references=["Stull (1988) Boundary Layer Meteorology", "ECMWF TKE Parameterization"],
        compute_func=lambda u_var, v_var, w_var: 0.5 * (u_var + v_var + w_var),
    ),
    EncyclopediaEntry(
        key="ekman_spiral",
        name="Spirale d'Ekman en Couche Limite",
        domain="Couche Limite Atmosphérique",
        equation="u(z) = Ug * (1 - exp(-a*z)*cos(a*z)) ; v(z) = Ug * exp(-a*z)*sin(a*z)",
        latex_equation=r"u(z) = U_g \left(1 - e^{-az}\cos az\right), \quad v(z) = U_g e^{-az}\sin az",
        variables={"Ug": "Vent géostrophique au-dessus de la couche limite", "a": "sqrt(f / (2*Km))"},
        units={"u, v": "m/s", "z": "m"},
        description="Rotation progressive et augmentation de l'intensité du vent avec l'altitude sous l'effet du frottement au sol et de Coriolis.",
        application_conditions=["Couche limite laminaire/turbulente stationnaire"],
        limitations=["Viscosité turbulente Km supposée constante"],
        references=["Ekman (1905)", "Stull (1988)"],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
