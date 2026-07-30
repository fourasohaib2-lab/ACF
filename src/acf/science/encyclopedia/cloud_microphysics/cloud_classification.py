"""
Complete WMO Cloud Classification Encyclopedia Module
"""

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

WMO_GENRES = [
    {
        "key": "wmo_cirrus",
        "name": "Cirrus (Ci)",
        "altitude_range_m": (6000, 12000),
        "typical_temp_c": (-60, -35),
        "composition": "Glace pure",
        "precipitation": "Aucune au sol (Virga glacée)",
        "aviation_hazard": "Turbulence légère à modérée, Cristaux de glace",
        "satellite_signature": "Forte transparence en canal visible, Froid en IR 10.8µm",
    },
    {
        "key": "wmo_cirrostratus",
        "name": "Cirrostratus (Cs)",
        "altitude_range_m": (6000, 12000),
        "typical_temp_c": (-50, -30),
        "composition": "Glace pure",
        "precipitation": "Aucune au sol (Halo solaire/lunaire)",
        "aviation_hazard": "Léger givrage en sommet",
        "satellite_signature": "Voile fin homogène en IR",
    },
    {
        "key": "wmo_cirrocumulus",
        "name": "Cirrocumulus (Cc)",
        "altitude_range_m": (6000, 10000),
        "typical_temp_c": (-40, -25),
        "composition": "Glace et gouttelettes surfondues",
        "precipitation": "Aucune",
        "aviation_hazard": "Turbulence légère (ondes)",
        "satellite_signature": "Champs ridés à haute altitude",
    },
    {
        "key": "wmo_altostratus",
        "name": "Altostratus (As)",
        "altitude_range_m": (2000, 7000),
        "typical_temp_c": (-25, 0),
        "composition": "Mélange eau surfondue et glace",
        "precipitation": "Pluie ou neige continue modérée",
        "aviation_hazard": "Givrage modéré à séchage rapide",
        "satellite_signature": "Gris continu en VIS, température moyenne en IR",
    },
    {
        "key": "wmo_altocumulus",
        "name": "Altocumulus (Ac)",
        "altitude_range_m": (2000, 6000),
        "typical_temp_c": (-20, 5),
        "composition": "Eau surfondue prédominante",
        "precipitation": "Virga occasionnelle",
        "aviation_hazard": "Givrage modéré, turbulence en onde",
        "satellite_signature": "Texture d'éléments globuleux en VIS",
    },
    {
        "key": "wmo_stratus",
        "name": "Stratus (St)",
        "altitude_range_m": (0, 2000),
        "typical_temp_c": (-5, 15),
        "composition": "Gouttelettes d'eau liquide",
        "precipitation": "Bruine, neige en grain",
        "aviation_hazard": "Plafond très bas, Visi réduite",
        "satellite_signature": "Très brillant en VIS, chaud en IR (proche du sol)",
    },
    {
        "key": "wmo_stratocumulus",
        "name": "Stratocumulus (Sc)",
        "altitude_range_m": (500, 2500),
        "typical_temp_c": (-10, 15),
        "composition": "Eau liquide et surfondue",
        "precipitation": "Pluie faible ou neige légère",
        "aviation_hazard": "Givrage en basse couche",
        "satellite_signature": "Mosaïque de galets sombres et clairs",
    },
    {
        "key": "wmo_cumulus",
        "name": "Cumulus (Cu)",
        "altitude_range_m": (600, 3000),
        "typical_temp_c": (0, 20),
        "composition": "Eau liquide",
        "precipitation": "Averses faibles en Cu congestus",
        "aviation_hazard": "Turbulence convective en basses couches",
        "satellite_signature": "Petits éléments très brillants en VIS",
    },
    {
        "key": "wmo_cumulonimbus",
        "name": "Cumulonimbus (Cb)",
        "altitude_range_m": (500, 15000),
        "typical_temp_c": (-60, 25),
        "composition": "Eau liquide sol, surfondue centre, glace sommet",
        "precipitation": "Averses violentes, grêle, orages",
        "aviation_hazard": "SEV Givrage, Cisaillement, Foudre, Severe CAT, Grêle",
        "satellite_signature": "Sommet très froid (< -60°C en IR), Enclume massive en VIS",
    },
]

for g in WMO_GENRES:
    entry = EncyclopediaEntry(
        key=g["key"],
        name=f"Genre OMM: {g['name']}",
        domain="Nuages & Microphysique",
        subdomain="Classification WMO",
        equation=f"Altitude: {g['altitude_range_m'][0]}-{g['altitude_range_m'][1]} m",
        latex_equation=rf"\text{{{g['name']}}} \quad h \in [{g['altitude_range_m'][0]}, {g['altitude_range_m'][1]}] \text{{ m}}",
        variables={
            "Altitude": f"{g['altitude_range_m']} m",
            "Température": f"{g['typical_temp_c']} °C",
            "Composition": g["composition"],
        },
        units={"Altitude": "m", "Température": "°C"},
        description=f"Genre nuageux WMO. Précipitation: {g['precipitation']}. Danger aéronautique: {g['aviation_hazard']}.",
        application_conditions=["Observation météorologique WMO International Cloud Atlas"],
        limitations=["Dépend des conditions régionales et thermiques"],
        references=["WMO International Cloud Atlas (2017)", "ICAO Annex 3"],
    )
    EncyclopediaRegistry.register(entry)


class WMOCloudClassifier:
    """
    Classificateur scientifique d'espèces nuageuses OMM.
    """

    def classify_genre(self, base_m: float, temp_c: float, vertical_extension_m: float) -> str:
        if vertical_extension_m > 6000 and temp_c < 0:
            return "Cumulonimbus (Cb)"
        if base_m > 6000:
            return "Cirrus / Cirrostratus / Cirrocumulus"
        if base_m > 2000:
            return "Altostratus / Altocumulus"
        return "Stratus / Stratocumulus / Cumulus"
