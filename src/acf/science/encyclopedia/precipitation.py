"""
Precipitation Science Encyclopedia Domain
"""

import math
from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

ENTRIES = [
    EncyclopediaEntry(
        key="terminal_velocity_raindrops",
        name="Vitesse Limite de Chute des Gouttes de Pluie",
        domain="Précipitations",
        subdomain="Chute des hydrométéores",
        equation="vt(D) = 9.65 - 10.3 * exp(-600 * D)",
        latex_equation=r"v_t(D) = 9.65 - 10.3 e^{-600 D}",
        variables={"D": "Diamètre de la goutte de pluie (m)", "vt": "Vitesse limite de chute (m/s)"},
        units={"D": "m", "vt": "m/s"},
        description="Vitesse maximale atteinte par une goutte de pluie lorsque la gravité équilibre la traînée de l'air.",
        application_conditions=["Précipitations de pluie sous pression atmosphérique standard"],
        limitations=["Valable pour diamètres D entre 0.5 mm et 5.0 mm"],
        references=["Marshall & Palmer (1948)", "Atlas et al. (1973)"],
        compute_func=lambda diameter_m: 9.65 - 10.3 * math.exp(-600.0 * diameter_m),
    ),
    EncyclopediaEntry(
        key="subcloud_evaporation",
        name="Évaporation Sous-Nuageuse (Virga)",
        domain="Précipitations",
        subdomain="Processus thermodynamiques",
        equation="E_virga = k_evap * (1 - RH) * qr**0.52",
        latex_equation=r"E_{virga} = k_{evap} (1 - RH) q_r^{0.52}",
        variables={"RH": "Humidité relative sous le nuage", "qr": "Contenu en eau de pluie"},
        units={"E_virga": "kg/(kg·s)"},
        description="Évaporation des gouttes de pluie traversant une couche d'air sous-saturée sous la base du nuage.",
        application_conditions=["Couche sous-nuageuse sèche"],
        limitations=["Refroidissement évaporatif entraînant des dévalements d'air (downbursts)"],
        references=["Kessler (1969)", "Rogers & Yau (1989)"],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
