"""
Advanced Turbulence & Boundary Layer Modeling Encyclopedia Module
"""

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

ENTRIES = [
    EncyclopediaEntry(
        key="tke_prognostic_equation",
        name="Équation de Bilan de l'Énergie Cinétique Turbulente (TKE)",
        domain="Turbulence Avancée",
        subdomain="Paramétrisation de la turbulence",
        equation="de/dt = P_shear + P_buoyancy + Transports - dissipation_epsilon",
        latex_equation=r"\frac{\partial e}{\partial t} = -\overline{u^\prime w^\prime}\frac{\partial U}{\partial z} + \frac{g}{\theta_0}\overline{w^\prime \theta^\prime} - \frac{\partial}{\partial z}\left(\overline{w^\prime e} + \frac{\overline{w^\prime p^\prime}}{\rho_0}\right) - \varepsilon",
        variables={"P_shear": "Production mécanique par cisaillement", "P_buoyancy": "Production/destruction par flottabilité", "epsilon": "Taux de dissipation visqueuse"},
        units={"e": "m²/s²", "epsilon": "m²/s³"},
        description="Équation différentielle décrivant l'évolution temporelle de la TKE dans les modèles NWP (ex: scheme EDMF dans AROME).",
        application_conditions=["Modélisation de la couche limite atmosphérique (1.5 order closure)"],
        limitations=["Hypothèses de fermeture pour les termes d'ordre supérieur (3ème ordre)"],
        references=["Stull (1988) Boundary Layer Meteorology", "Mellor & Yamada (1982) Rev. Geophys."],
    ),
    EncyclopediaEntry(
        key="richardson_number_gradient",
        name="Nombre de Richardson de Gradient (Ri)",
        domain="Turbulence Avancée",
        subdomain="Stabilité de l'écoulement",
        equation="Ri = (g / theta) * (dtheta/dz) / (dU/dz)^2",
        latex_equation=r"Ri = \frac{\frac{g}{\theta_0}\frac{\partial \theta}{\partial z}}{\left(\frac{\partial U}{\partial z}\right)^2}",
        variables={"g": "9.81 m/s²", "dtheta/dz": "Gradient de température potentielle", "dU/dz": "Cisaillement du vent"},
        units={"Ri": "dimensionless"},
        description="Rapport entre la stabilité thermique et la production mécanique par cisaillement. Ri < 0.25 (critique) indique un déclenchement de la turbulence.",
        application_conditions=["Écoulements stratifiés en cisaillement"],
        limitations=["Turbulence intermittente au-delà du Ri critique"],
        references=["Richardson (1920) Proc. R. Soc. Lond.", "Holton & Hakim (2012)"],
        compute_func=lambda g_over_theta, dtheta_dz, du_dz: (g_over_theta * dtheta_dz) / max(du_dz ** 2, 1e-8),
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
