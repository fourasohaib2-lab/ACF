"""
ICAO & WMO Aviation Observations Encyclopedia Module (METAR, SPECI, TAF, AMDAR, ACARS)
"""

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

ENTRIES: list[EncyclopediaEntry] = [
    EncyclopediaEntry(
        key="metar_speci_aviation_observation",
        name="Rapport Météorologique d'Aérodrome METAR / SPECI (OACI Annexe 3 / WMO FM-15)",
        domain="Systèmes d'Observation Météorologique",
        subdomain="Météorologie Aéronautique",
        equation="Format codé standardisé: CCCC YYGGggZ dddffKT CAVOK/VV hhh T'T'/T'dT'd QPPPP NOSIG/TREND",
        latex_equation=r"\text{METAR} \implies (\text{Vent}, \text{Visibilité RVR}, \text{Temps présent}, \text{Nuages/Plafond}, T, T_d, \text{QNH})",
        variables={
            "Wind": "Direction (deg) et Vitesse (kt)",
            "RVR": "Runway Visual Range (m)",
            "Clouds": "Couverture (FEW, SCT, BKN, OVC) et hauteur (ft)",
            "QNH": "Altimètre (hPa)",
        },
        units={"Wind": "kt", "Vis": "m", "Cloud_Height": "ft", "QNH": "hPa"},
        description="Message d'observation régulière (METAR) ou spéciale (SPECI) diffusé toutes les 30 min sur tous les aéroports du monde. Fournit les paramètres de sécurité indispensables à l'aviation civile.",
        application_conditions=[
            "Protection de la navigation aérienne, décollage/atterrissage et assimilation d'aérodrome"
        ],
        limitations=["Zone de mesure restreinte au périmètre immédiat de la piste de l'aérodrome"],
        references=["ICAO Annex 3 Meteorological Service for International Air Navigation", "WMO-No. 782"],
    ),
    EncyclopediaEntry(
        key="amdar_acars_aircraft_observation",
        name="Observations d'Avions de Ligne AMDAR / ACARS (WMO AMDAR Programme)",
        domain="Systèmes d'Observation Météorologique",
        subdomain="Observations Aériennes",
        equation="Mesures automatiques de vent (u,v), température (T) et turbulence (EDR) par la flotte commerciale",
        latex_equation=r"\text{AMDAR} \implies (\text{Lat}, \text{Lon}, \text{Pression/Alt}, T, \mathbf{V}, \text{EDR}, q_{\text{vapeur}})",
        variables={
            "T": "Temperature de l'air extérieure (K)",
            "V": "Vecteur vent (m/s)",
            "EDR": "Equivalent Eddy Dissipation Rate (Turbulence)",
        },
        units={"T": "K", "Wind": "m/s", "EDR": "m^(2/3)/s"},
        description="Relais automatique de données météorologiques de haute précision mesurées en continu par les sondes des avions commerciaux en phase de montée, descente et vol de croisière. Impact majeur dans les NWP.",
        application_conditions=[
            "Assimilation synoptique haute résolution 4D-Var / EnVar dans IFS, AROME, GFS, Rapid Refresh"
        ],
        limitations=["Disponibilité réduite la nuit et absence de couverture dans les zones non survolées"],
        references=["WMO AMDAR Reference Manual (WMO-No. 958)", "Moninger et al. (2010) BAMS"],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
