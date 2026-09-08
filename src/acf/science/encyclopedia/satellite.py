"""
Meteorological Satellite Sensing Encyclopedia Domain
"""

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

ENTRIES = [
    EncyclopediaEntry(
        key="geostationary_satellite_imagery",
        name="Imagerie Satellite Géostationnaire (Meteosat / GOES / Himawari)",
        domain="Satellites Météorologiques",
        subdomain="Télédétection spatiale",
        equation="Sub-satellite point on equator (35,786 km altitude), 15-min scan frequency",
        latex_equation=r"R_{\text{geo}} = 42,164 \text{ km from Earth center}",
        variables={"Canaux": "VIS (0.6 µm), IR (10.8 µm), WV (6.2 µm)"},
        units={"Canaux": "µm"},
        description="Satellites en orbite géostationnaire fournissant une surveillance continue de l'évolution des nuages et de la vapeur d'eau.",
        application_conditions=["Observation synoptique des latitudes moyennes et équatoriales (70°N - 70°S)"],
        limitations=["Résolution spatiale plus faible aux très hautes latitudes/pôles"],
        references=["EUMETSAT Meteosat User Guide", "NOAA GOES-R Series Technical Manual"],
    ),
    EncyclopediaEntry(
        key="water_vapor_satellite_channel",
        name="Canal Absorption Vapeur d'Eau (6.2 µm / 7.3 µm)",
        domain="Satellites Météorologiques",
        subdomain="Canaux spectraux",
        equation="BT_wv = T_eff of upper tropospheric water vapor layer",
        latex_equation=r"BT_{\text{WV}} \propto \int B_\lambda(T(z)) \frac{d\tau_{\text{WV}}}{dz} dz",
        variables={
            "BT": "Température de brillance (K)",
            "WV": "Absorption par la bande de vibration de l'eau à 6.2 µm",
        },
        units={"BT": "K"},
        description="Canal satellite mesurant le rayonnement émis par la vapeur d'eau dans la moyenne et haute troposphère (détection des thalwegs et jet-stream).",
        application_conditions=["Troposphère moyenne et haute (400-200 hPa)"],
        limitations=["Opacité de la vapeur d'eau masquant la basse troposphère"],
        references=["EUMETSAT Training Guides", "WMO Satellite Meteorology"],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
