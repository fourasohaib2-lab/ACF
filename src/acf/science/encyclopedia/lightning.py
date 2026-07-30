"""
Lightning Physics & Atmospheric Electrification Encyclopedia Module
"""

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

ENTRIES = [
    EncyclopediaEntry(
        key="non_inductive_cloud_charging",
        name="Électrification Non-Inductive par Collision Glace-Graupel",
        domain="Foudre & Électricité Atmosphérique",
        subdomain="Physique de l'orage",
        equation="delta_q = f(T, LWC, v_rel)",
        latex_equation=r"\Delta q = q_{\text{graupel}} - q_{\text{crystal}} \propto f(T, \text{LWC})",
        variables={"T": "Température de la zone de givrage (-10 à -20°C)", "LWC": "Liquid Water Content (g/m³)"},
        units={"delta_q": "pC par collision"},
        description="Transfert de charge électrique lors du choc entre des cristaux de glace légers (se chargeant positivement) et des graupels plus lourds (se chargeant négativement).",
        application_conditions=["Zone de coexistence eau surfondue / glace / graupel entre -10°C et -20°C"],
        limitations=["Inversion du signe de charge à la température de déflexion Tr (~ -15°C)"],
        references=["Takahashi (1978) J. Atmos. Sci.", "Saunders et al. (1991)"],
    ),
    EncyclopediaEntry(
        key="lightning_flash_rate_price_rind",
        name="Paramétrisation du Taux d'Éclairs de Price & Rind",
        domain="Foudre & Électricité Atmosphérique",
        subdomain="Paramétrisation des orages",
        equation="F_continental = 3.44e-5 * H_top^4.9",
        latex_equation=r"F_{\text{flash}} = 3.44 \times 10^{-5} H_{\text{top}}^{4.9}",
        variables={"Htop": "Hauteur du sommet du nuage Cumulonimbus (km)"},
        units={"F_flash": "éclairs / min"},
        description="Relation puissance reliant la hauteur de la tour convective d'un Cumulonimbus à la fréquence de la foudre.",
        application_conditions=["Convection profonde continentale"],
        limitations=["Coefficient 5 fois plus faible pour les orages maritimes"],
        references=["Price & Rind (1992) Geophys. Res. Lett.", "WMO Lightning Detection Guide"],
        compute_func=lambda cloud_top_height_km: 3.44e-5 * (cloud_top_height_km ** 4.9),
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
