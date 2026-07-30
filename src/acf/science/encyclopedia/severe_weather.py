"""
Severe Weather & Storm Kinematics Encyclopedia Module
"""

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

ENTRIES = [
    EncyclopediaEntry(
        key="storm_relative_helicity_srh",
        name="Hélicité Relative à l'Orage (SRH)",
        domain="Phénomènes Violents & Grêle",
        subdomain="Cinématique des orages",
        equation="SRH = - int (V - c) x (dV/dz) dz",
        latex_equation=r"\text{SRH} = -\int_{0}^{z} (\mathbf{V} - \mathbf{c}) \cdot \boldsymbol{\omega}_h \, dz",
        variables={"V": "Profil du vent environnemental (m/s)", "c": "Vitesse du déplacement de l'orage (m/s)", "omega_h": "Vorticité horizontale (s⁻¹)"},
        units={"SRH": "m²/s²"},
        description="Mesure du potentiel de rotation du courant ascendant d'un orage alimenté par le cisaillement du vent en basse couche.",
        application_conditions=["Prévision des supercellules et des tornades dans la couche 0-1 km ou 0-3 km"],
        limitations=["Sensible à la précision du vecteur de déplacement de l'orage c"],
        references=["Davies-Jones et al. (1990)", "NOAA SPC Severe Weather Manual"],
        compute_func=lambda u_shear, v_shear, storm_u, storm_v: (u_shear * storm_v) - (v_shear * storm_u),
    ),
    EncyclopediaEntry(
        key="derecho_windstorm",
        name="Derecho (Système Convectif de Rafales Devastatrices)",
        domain="Phénomènes Violents & Grêle",
        subdomain="Systèmes Convectifs de Meso-échelle (MCS)",
        equation="Swath length > 400 km with wind gusts > 26 m/s (50 kt)",
        latex_equation=r"\text{Length} \ge 400 \text{ km}, \quad V_{\text{gust}} \ge 26 \text{ m/s}",
        variables={"Longueur du couloir": "> 400 km", "Vitesse de rafale": "> 26 m/s"},
        units={"Vitesse": "m/s", "Longueur": "km"},
        description="Événement rare de vent convectif généralisé à déplacement rapide associé à un écho en arc (bow echo) sous un MCS.",
        application_conditions=["Environnements à fort CAPE, air sec en moyenne troposphère et fort cisaillement"],
        limitations=["Nécessite la persistance d'une ligne d'orages sur plusieurs heures"],
        references=["Johns & Hirt (1987) Wea. Forecasting", "WMO Severe Weather Docs"],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
