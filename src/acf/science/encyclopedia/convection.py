"""
Convection & Severe Storms Encyclopedia Domain
"""

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

ENTRIES = [
    EncyclopediaEntry(
        key="cape_encyclopedia",
        name="Énergie Potentielle Convective Disponible (CAPE)",
        domain="Convection & Orages",
        subdomain="Instabilité thermodynamique",
        equation="CAPE = int_(LFC)^(EL) g * (Tparcel - Tenv) / Tenv dz",
        latex_equation=r"\text{CAPE} = \int_{\text{LFC}}^{\text{EL}} g \frac{T_{\text{parcel}} - T_{\text{env}}}{T_{\text{env}}} dz",
        variables={"Tparcel": "Température parcelle (K)", "Tenv": "Température environnement (K)", "g": "9.81 m/s²"},
        units={"CAPE": "J/kg"},
        description="Mesure de l'énergie maximale disponible pour l'accélération verticale des courants ascendants convectifs.",
        application_conditions=["Sondages atmosphériques et convection profonde"],
        limitations=["Sensible au choix du niveau de départ de la parcelle (surface vs mean-layer)"],
        references=["WMO Severe Weather Manual", "Moncrieff & Miller (1976)"],
        compute_func=lambda dt_avg, dz, t_env_avg, g=9.81: g * (dt_avg / t_env_avg) * dz,
    ),
    EncyclopediaEntry(
        # NOTE (correction - registry key collision): renamed from
        # "supercell_thunderstorm" (also used, independently, by
        # severe_weather.py's mesocyclone-vorticity-form entry) so both
        # formulations are independently accessible instead of one
        # silently shadowing the other depending on import order. See
        # EncyclopediaRegistry.register()'s collision guard.
        key="supercell_thunderstorm_overview",
        name="Orage Supercellulaire",
        domain="Convection & Orages",
        subdomain="Structure orageuse",
        equation="Mesocyclone Rotation: SCP = (CAPE/1000)*(SRH/50)*(BulkShear/20)",
        latex_equation=r"\text{SCP} = \left(\frac{\text{CAPE}}{1000}\right) \left(\frac{\text{SRH}}{50}\right) \left(\frac{\Delta V_{0-6}}{20}\right)",
        variables={
            "CAPE": "J/kg",
            "SRH": "Hélicité relative à l'orage (m²/s²)",
            "BulkShear": "Cisaillement 0-6 km (m/s)",
        },
        units={"SCP": "dimensionless"},
        description="Cellule orageuse possédant un courant ascendant en rotation quasi-permanente (mésocyclone).",
        application_conditions=["Environnements à fort CAPE et fort cisaillement vertical du vent"],
        limitations=["Nécessite la résolution spatiale des mésocyclones (< 2 km)"],
        references=["Browning (1964)", "Doswell & Evans (2003)"],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
