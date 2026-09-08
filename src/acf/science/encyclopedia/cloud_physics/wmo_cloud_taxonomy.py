"""
WMO Cloud Taxonomy, Species, Varieties, Supplementary Features & Secondary Ice Production Encyclopedia Module
"""

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

# ---------------------------------------------------------------------------
# Computational Functions for Cloud Taxonomy & Microphysics
# ---------------------------------------------------------------------------


def calculate_hallett_mossop_splintering(temp_c: float, rime_rate_mg_s: float) -> float:
    """Calcul du taux de production de fragments de glace par le mécanisme de Hallett-Mossop (Rime-splintering).

    NOTE (correction): the efficiency previously used a single symmetric tent
    centered at -5.5°C (`abs(temp_c + 5.5) / 2.5`), which is the geometric
    midpoint of the [-8, -3] window, not the actual peak. Hallett & Mossop
    (1974) and subsequent literature (verified via WebSearch) place the peak
    splintering rate "near -5°C" within the asymmetric [-8, -3] window - the
    comment already said "-5°C" but the formula's true peak was -5.5°C.
    Replaced with a piecewise-linear efficiency that genuinely peaks at -5°C:
    rising from 0 at -8°C to 1 at -5°C (3°C-wide rising limb), then falling
    from 1 at -5°C to 0 at -3°C (2°C-wide falling limb).
    """
    if not (-8.0 <= temp_c <= -3.0) or rime_rate_mg_s <= 0.0:
        return 0.0
    # Taux maximal à -5°C (~ 350 fragments par mg de givre accrété)
    if temp_c <= -5.0:
        efficiency = (temp_c + 8.0) / 3.0
    else:
        efficiency = (-3.0 - temp_c) / 2.0
    efficiency = max(0.0, min(1.0, efficiency))
    return 350.0 * rime_rate_mg_s * efficiency


# ---------------------------------------------------------------------------
# Encyclopedia Entries
# ---------------------------------------------------------------------------

ENTRIES: list[EncyclopediaEntry] = [
    EncyclopediaEntry(
        key="wmo_cloud_species_classification",
        name="Espèces Nuageuses de l'OMM (WMO Cloud Species)",
        domain="Physique des Nuages",
        subdomain="Taxonomie WMO",
        equation="Taxonomie OMM: Genre + Espèce + Variété",
        latex_equation=r"\text{Nuage} = \text{Genre} \oplus \text{Espèce (fibratus, lenticularis, castellanus, congestus...)}",
        variables={
            "Espèces principales": "fibratus, uncinus, spissatus, castellanus, lenticularis, congestus, humilis, mediocris, fractus"
        },
        units={"Classification": "WMO Code Table 0500"},
        description="Subdivision taxonomique officielle des 10 genres de nuages basée sur la forme, la structure interne et l'organisation mécanique.",
        application_conditions=[
            "Observation météorologique internationale (WMO-No. 407 Atlas International des Nuages)"
        ],
        limitations=[
            "Nécessite une observation visuelle qualifiée ou une analyse d'images satellitaires haute résolution"
        ],
        references=["WMO-No. 407 International Cloud Atlas (2017)", "WMO Manual on Codes"],
    ),
    EncyclopediaEntry(
        key="wmo_supplementary_features_asperitas",
        name="Particularités Supplémentaires et Nuages Annexe (Asperitas, Mammatus, Arcus, Virga)",
        domain="Physique des Nuages",
        subdomain="Taxonomie WMO",
        equation="Structures sous-nuageuses: Asperitas, Mamma, Arcus, Virga, Tuba, Incus",
        latex_equation=r"\text{Feature} \in \{\text{asperitas}, \text{mamma}, \text{arcus}, \text{virga}, \text{tuba}, \text{incus}\}",
        variables={
            "Mamma": "Poches de subsidence sous l'enclume",
            "Asperitas": "Ondulations chaotiques sous la base nuageuse",
            "Arcus": "Rouleau frontal de rafales",
        },
        units={"Particularités": "WMO Code Table"},
        description="Structures morphologiques remarquables attachées ou sous-jacentes aux nuages principaux indiquant des processus dynamiques intenses (subsidence, onde de gravité, cisaillement).",
        application_conditions=["Précipitation, turbulence sévère et orages"],
        limitations=["Signature visuelle spectaculaire mais de courte durée"],
        references=["WMO-No. 407 (2017)", "AMS Cloud Atlas"],
    ),
    EncyclopediaEntry(
        key="pyrocumulonimbus_cloud",
        name="Pyrocumulonimbus (PyroCb)",
        domain="Physique des Nuages",
        subdomain="Nuages spéciaux",
        equation="Orage généré par le feu: Convection thermique extrême poussée par un incendie de forêt",
        latex_equation=r"\text{PyroCb} \implies \text{Heat}_{\text{fire}} + \text{Moisture}_{\text{combustion}} \to \text{Tropopause Injection}",
        variables={
            "Soot_aerosols": "Suies servant d'INP/CCN massifs",
            "Altitude_injection": "10 à 18 km (Stratosphère)",
        },
        units={"Altitude": "km"},
        description="Cumulonimbus d'une violence extrême généré par le chauffage intense et les cendres d'un incendie de forêt majeur, capable d'injecter des suies et des aérosols directement dans la stratosphère.",
        application_conditions=["Grands incendies de forêt (Australie, Californie, Sibérie)"],
        limitations=["Génère de la foudre susceptible d'allumer de nouveaux foyers d'incendie en aval (Dry lightning)"],
        references=["Fromm et al. (2010) Bull. Amer. Meteor. Soc.", "WMO Special Clouds"],
    ),
    EncyclopediaEntry(
        key="noctilucent_polar_stratospheric_clouds",
        name="Nuages Mésosphériques Lumineux / Noctiluques (Noctilucent / PSC)",
        domain="Physique des Nuages",
        subdomain="Nuages spéciaux",
        equation="Altitude 80 - 85 km (Mésopause polaire), T < -120°C (150 K)",
        latex_equation=r"h_{\text{cloud}} \approx 83 \text{ km}, \quad T \le 150 \text{ K}, \quad \text{Cristaux de glace ultra-fins (r < 50 nm)}",
        variables={"Altitude": "80 à 85 km", "Composition": "Glace d'eau sur poussières météoriques"},
        units={"Altitude": "km"},
        description="Les nuages les plus hauts de l'atmosphère terrestre, situés dans la mésosphère près de la mésopause polaire d'été. Visibles au crépuscule sous éclairement solaire rasant.",
        application_conditions=["Hautes latitudes polaires en été"],
        limitations=["Observables uniquement la nuit lorsque le soleil est entre 6° et 16° sous l'horizon"],
        references=["WMO-No. 407", "Gadsden & Schröder (1989) Noctilucent Clouds"],
    ),
    EncyclopediaEntry(
        key="hallett_mossop_secondary_ice_production",
        name="Production Secondaire de Glace par l'Effet Hallett-Mossop",
        domain="Physique des Nuages",
        subdomain="Microphysique",
        equation="Rime-splintering à -3°C <= T <= -8°C: ~ 350 fragments de glace par mg de givre accrété",
        latex_equation=r"\left.\frac{dN_{\text{ice}}}{dt}\right|_{\text{HM}} = 3.5 \times 10^8 f(T) \cdot \left.\frac{dq_g}{dt}\right|_{\text{riming}} \quad (T \in [-3,-8]^\circ\text{C})",
        variables={
            "T": "Température zone de givrage (-3°C à -8°C)",
            "dqg/dt": "Taux d'accrétion de gouttes surfrondues sur graupel",
        },
        units={"N_ice": "m⁻³·s⁻¹"},
        description="Processus de multiplication secondaire de la glace par éclatement des gouttes d'eau surfondue au moment de leur congélation à la surface des graupels (rime-splintering). Explique les fortes concentrations de glace observées dans les nuages convectifs.",
        application_conditions=[
            "Zone de givrage convective entre -3°C et -8°C avec présence simultanée de petites et grosses gouttes"
        ],
        limitations=["Inexistant en dehors de la fenêtre thermique stricte [-3°C, -8°C]"],
        references=["Hallett & Mossop (1974) Nature", "Pruppacher & Klett (1997)"],
        compute_func=calculate_hallett_mossop_splintering,
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
