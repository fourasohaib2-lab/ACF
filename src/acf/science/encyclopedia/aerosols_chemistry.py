"""
Aerosols & Atmospheric Chemistry Encyclopedia Domain
"""

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

ENTRIES = [
    EncyclopediaEntry(
        key="tropospheric_ozone_photostationary_state",
        name="État Photostationnaire de l'Ozone Troposphérique",
        domain="Aérosols & Chimie",
        subdomain="Chimie atmosphérique",
        equation="[O3] = (j_NO2 * [NO2]) / (k_O3_NO * [NO])",
        latex_equation=r"[\text{O}_3] = \frac{j_{\text{NO}_2} [\text{NO}_2]}{k_{\text{O}_3+\text{NO}} [\text{NO}]}",
        variables={"j_NO2": "Taux de photolyse du NO2", "k": "Constante de réaction NO + O3"},
        units={"[O3]": "ppb"},
        description="Équilibre chimique rapide sous rayonnement solaire entre l'ozone, le monoxyde et le dioxyde d'azote (Cycle de Leighton).",
        application_conditions=["Troposphère ensoleillée sans COV massifs"],
        limitations=["Perturbé par la chimie des radicaux peroxydes (RO2)"],
        references=["Seinfeld & Pandis (2016) Atmospheric Chemistry and Physics", "WMO GAW Reports"],
    ),
    EncyclopediaEntry(
        key="dry_deposition_velocity",
        name="Vitesse de Dépôt Sec des Aérosols",
        domain="Aérosols & Chimie",
        subdomain="Dépôt et transport",
        equation="vd = 1 / (Ra + Rb + Rc)",
        latex_equation=r"v_d = \frac{1}{R_a + R_b + R_c}",
        variables={
            "Ra": "Résistance aérodynamique",
            "Rb": "Résistance de sous-couche laminaire",
            "Rc": "Résistance de surface (canopée)",
        },
        units={"vd": "m/s"},
        description="Processus de capture des polluants et aérosols par la surface terrestre sans précipitation.",
        application_conditions=["Couche limite de surface"],
        limitations=["Dépend de la rugosité de surface et du diamètre des particules"],
        references=["Wesely (1989) Atmos. Environ.", "Seinfeld & Pandis (2016)"],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
