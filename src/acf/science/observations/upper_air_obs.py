"""
WMO Upper Air Observations Encyclopedia Module (Radiosondes, Dropsondes, GPS-RO, GNSS PWV, Profilers)
"""

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry


def calculate_atmospheric_refractivity(pressure_hpa: float, temperature_k: float, vapor_pressure_hpa: float) -> float:
    """
    Réfractivité atmosphérique (Smith & Weintraub 1953) :
    N = 77.6*(p/T) + 3.73e5*(e/T^2), en N-units.

    NOTE (correction): equation field is fully explicit but this entry
    had no compute_func.
    """
    if temperature_k <= 0.0:
        raise ValueError("temperature_k must be positive.")
    return 77.6 * (pressure_hpa / temperature_k) + 3.73e5 * (vapor_pressure_hpa / (temperature_k**2))


ENTRIES: list[EncyclopediaEntry] = [
    EncyclopediaEntry(
        key="radiosonde_temp_observation",
        name="Radiosondages et Sontages par Goutte DROPSONDE (WMO FM-35 TEMP / BUFR TM 309052)",
        domain="Systèmes d'Observation Météorologique",
        subdomain="Haute Atmosphère & Profils",
        equation="Profils verticaux haute résolution de P, T, U, Td et Vent de la surface jusqu'à 30 km",
        latex_equation=r"\text{TEMP} \implies \left\{ p(z), T(z), T_d(z), u(z), v(z) \right\}_{z=0}^{30\text{ km}}",
        variables={
            "p": "Pression (Pa)",
            "T": "Température (K)",
            "Td": "Point de rosée (K)",
            "Wind": "Vecteur vent zonal/méridien (m/s)",
        },
        units={"p": "Pa", "T": "K", "Wind": "m/s"},
        description="Mesure directe in-situ de la structure thermodynamique et dynamique de la troposphère et de la stratosphère. Considéré comme la référence absolue (Ground Truth) pour l'étalonnage et la validation NWP.",
        application_conditions=["Assimilation 3D-Var / 4D-Var, diagrammes thermodynamiques (Emagramme, Skew-T)"],
        limitations=["Lancement généralement restreint aux heures synoptiques 00 et 12 UTC"],
        references=["WMO-No. 8 Guide to Instruments", "GUAN (GCOS Upper-Air Network) Standards"],
    ),
    EncyclopediaEntry(
        key="gps_radio_occultation_gnss_pwv",
        name="Radio-Occultation GPS (GPS-RO) et Contenu Intégré en Vapeur d'Eau GNSS PWV",
        domain="Systèmes d'Observation Météorologique",
        subdomain="Télédétection GNSS",
        equation="Réfraction des signaux GNSS à travers l'atmosphère: Réfractivité N = 77.6 (p/T) + 3.73e5 (e/T²)",
        latex_equation=r"N = 77.6 \frac{p}{T} + 3.73 \times 10^5 \frac{e}{T^2}",
        variables={"N": "Réfractivité atmosphérique adimensionnelle (N-units)", "PWV": "Precipitable Water Vapor (mm)"},
        units={"N": "N-units", "PWV": "mm"},
        description="Sondage mondial hautement précis de la température et de l'humidité atmosphérique mesuré par le retard et la courbure des signaux GPS/GNSS captés par des microsatellites (COSMIC-2, Spire, MetOp).",
        application_conditions=[
            "Assimilation sans biais des profils thermiques dans la stratosphère et la troposphère haute"
        ],
        limitations=["Résolution horizontale le long de la ligne de visée de l'ordre de 100 à 300 km"],
        references=["Kursinski et al. (1997) J. Geophys. Res.", "Rocken et al. (1997) Geophys. Res. Lett."],
        compute_func=calculate_atmospheric_refractivity,
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
