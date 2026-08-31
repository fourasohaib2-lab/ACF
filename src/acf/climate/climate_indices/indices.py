"""
Atmospheric Complexity Framework (ACF)

Climate Indices & Teleconnection Patterns Module
(ENSO, ONI, SOI, PDO, AMO, NAO, AO, SAM, MJO, QBO, IOD, SPI, SPEI, PDSI, Fire Weather Index)
"""

from dataclasses import dataclass


@dataclass
class ClimateIndexInfo:
    """Description scientifique d'un indice climatique ou mode de téléconnexion."""

    key: str
    name: str
    domain: str
    region: str
    calculation_method: str
    latex_formula: str
    physical_impacts: list[str]
    references: list[str]


CLIMATE_INDICES_REGISTRY: dict[str, ClimateIndexInfo] = {
    "enso_nino34": ClimateIndexInfo(
        key="enso_nino34",
        name="El Niño / Southern Oscillation (NINO3.4 & ONI)",
        domain="Couplage Océan-Atmosphère Tropical",
        region="Pacifique Équatorial (5°N-5°S, 170°W-120°W)",
        calculation_method="Anomalie moyenne de SST sur la zone NINO3.4 lissée sur 3 mois (Oceanic Niño Index)",
        latex_formula=r"\text{ONI} = \overline{\text{SST}_{\text{NINO3.4}} - \text{SST}_{\text{climatology}}}^{\,3\text{ mois}}",
        physical_impacts=[
            "El Niño (ONI >= +0.5°C) : Sécheresse en Indonésie/Australie, fortes pluies au Pérou/Chili, affaiblissement des alizés.",
            "La Niña (ONI <= -0.5°C) : Renforcement des alizés, résurgence d'eau froide à l'Est, mousson indienne renforcée.",
        ],
        references=["Trenberth (1997) Bull. Amer. Meteor. Soc. 78, 2771-2777"],
    ),
    "nao": ClimateIndexInfo(
        key="nao",
        name="North Atlantic Oscillation (NAO)",
        domain="Variabilité Synoptique & Climatologique",
        region="Atlantique Nord (Islande vs Açores)",
        calculation_method="Différence de pression réduite au niveau de la mer normalisée entre les Açores (Ponta Delgada) et l'Islande (Stykkisholmur)",
        latex_formula=r"\text{NAO} = \frac{P_{\text{Açores}} - \bar{P}_{\text{Açores}}}{\sigma_{\text{Açores}}} - \frac{P_{\text{Islande}} - \bar{P}_{\text{Islande}}}{\sigma_{\text{Islande}}}",
        physical_impacts=[
            "NAO+ : Dépression d'Islande très creuse, anticyclone des Açores puissant. Tempêtes et douceur sur le Nord de l'Europe, sécheresse sur le bassin Méditerranéen.",
            "NAO- : Gradient de pression faible, jet stream ondulant, poussées d'air arctique polaire vers l'Europe du Sud.",
        ],
        references=["Hurrell (1995) Science 269, 676-679"],
    ),
    "amo": ClimateIndexInfo(
        key="amo",
        name="Atlantic Multidecadal Oscillation (AMO)",
        domain="Variabilité Décennale Océanique",
        region="Bassin Atlantique Nord (0°-60°N, 80°W-0°)",
        calculation_method="Anomalie de température de surface de la mer (SST) dans l'Atlantique Nord sans la tendance du réchauffement global",
        latex_formula=r"\text{AMO} = \text{SST}_{\text{Atl. Nord}} - \text{Trend}_{\text{global}}",
        physical_impacts=[
            "AMO+ (Phase chaude) : Fréquence accrue des cyclones tropicaux intenses dans l'Atlantique, pluies au Sahel.",
            "AMO- (Phase froide) : Sécheresse prolongée au Sahel et réduction de l'activité cyclonique.",
        ],
        references=["Enfield et al. (2001) Geophys. Res. Lett. 28, 2077-2080"],
    ),
    "pdo": ClimateIndexInfo(
        key="pdo",
        name="Pacific Decadal Oscillation (PDO)",
        domain="Variabilité Décennale Pacifique",
        region="Pacifique Nord (au nord de 20°N)",
        calculation_method="Premier mode de variance EOF des anomalies de SST mensuelles dans le Pacifique Nord",
        latex_formula=r"\text{PDO} = \text{EOF}_1(\text{SST}_{\text{Pacifique Nord}})",
        physical_impacts=[
            "Modulation sur 20 à 30 ans du climat nord-américain et renforcement/atténuation des impacts de l'ENSO.",
        ],
        references=["Mantua et al. (1997) Bull. Amer. Meteor. Soc. 78, 1069-1079"],
    ),
    "spi_drought": ClimateIndexInfo(
        key="spi_drought",
        name="Standardized Precipitation Index (SPI - OMM Standard)",
        domain="Hydrologie & Sécheresse",
        region="Mondial",
        calculation_method="Transformation probabiliste Gamma des cumuls de précipitations sur 1, 3, 6, 12 ou 24 mois en distribution normale centrée réduite",
        latex_formula=r"\text{SPI} = \frac{H(x) - \mu}{\sigma}",
        physical_impacts=[
            "SPI <= -2.0 : Sécheresse extrême (Extreme Drought).",
            "SPI >= +2.0 : Humidité extrême (Extreme Wetness).",
        ],
        references=["McKee et al. (1993) Proc. 8th Conf. on Applied Climatology", "WMO-No. 1090 SPI User Guide"],
    ),
}


class ClimateIndicesEngine:
    """Moteur de recherche des indices climatiques et téléconnexions."""

    @classmethod
    def get(cls, key: str) -> ClimateIndexInfo | None:
        return CLIMATE_INDICES_REGISTRY.get(key.lower())

    @classmethod
    def list_indices(cls) -> list[str]:
        return list(CLIMATE_INDICES_REGISTRY.keys())
