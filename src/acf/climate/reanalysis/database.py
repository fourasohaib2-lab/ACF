"""
Atmospheric Complexity Framework (ACF)

Global Meteorological Reanalysis Database Module
(ERA5, ERA5-Land, ERA-Interim, MERRA-2, JRA-55, NCEP/NCAR CFSR, 20CR)
"""

from dataclasses import dataclass


@dataclass
class ReanalysisDatasetInfo:
    """Description d'un jeu de données de réanalyse météorologique/climatologique."""

    key: str
    name: str
    institution: str
    period: str
    spatial_resolution_deg: float
    vertical_levels: int
    temporal_resolution: str
    data_assimilation_system: str
    key_variables: list[str]
    references: list[str]


REANALYSIS_REGISTRY: dict[str, ReanalysisDatasetInfo] = {
    "era5": ReanalysisDatasetInfo(
        key="era5",
        name="ERA5 Reanalysis (ECMWF)",
        institution="ECMWF / Copernicus Climate Change Service (C3S)",
        period="1940 - Present",
        spatial_resolution_deg=0.25,  # ~31 km
        vertical_levels=137,
        temporal_resolution="Hourly",
        data_assimilation_system="4D-Var avec IFS Cy41r2",
        key_variables=["T", "U", "V", "Q", "Z", "MSLP", "2T", "10U", "10V", "TP", "SST", "CAPE", "IVT"],
        references=["Hersbach et al. (2020) Q. J. R. Meteorol. Soc. 146, 1999-2049"],
    ),
    "era5_land": ReanalysisDatasetInfo(
        key="era5_land",
        name="ERA5-Land (ECMWF)",
        institution="ECMWF / C3S",
        period="1950 - Present",
        spatial_resolution_deg=0.10,  # ~9 km
        vertical_levels=4,  # Niveaux de sol (0-7cm, 7-28cm, 28-100cm, 100-289cm)
        temporal_resolution="Hourly",
        data_assimilation_system="Forçage atmosphérique ERA5 + HTESSEL Land Surface Model",
        key_variables=["Soil Moisture", "Soil Temperature", "Snow Depth", "Evapotranspiration", "Runoff"],
        references=["Muñoz-Sabater et al. (2021) Earth Syst. Sci. Data 13, 4349-4383"],
    ),
    "merra2": ReanalysisDatasetInfo(
        key="merra2",
        name="MERRA-2 (Modern-Era Retrospective Analysis for Research and Applications v2)",
        institution="NASA Global Modeling and Assimilation Office (GMAO)",
        period="1980 - Present",
        spatial_resolution_deg=0.50,  # 0.5° x 0.625°
        vertical_levels=72,
        temporal_resolution="Hourly / 3-Hourly",
        data_assimilation_system="3D-Var Gridpoint Statistical Interpolation (GSI) + GEOS-5",
        key_variables=["Aerosol Optical Depth (AOD)", "Ozone", "TOA Radiation", "T", "U", "V", "Q"],
        references=["Gelaro et al. (2017) J. Climate 30, 5419-5554"],
    ),
    "jra55": ReanalysisDatasetInfo(
        key="jra55",
        name="JRA-55 (Japanese 55-year Reanalysis)",
        institution="Japan Meteorological Agency (JMA)",
        period="1958 - 2024",
        spatial_resolution_deg=0.56,  # TL319 (~60 km)
        vertical_levels=60,
        temporal_resolution="3-Hourly / 6-Hourly",
        data_assimilation_system="4D-Var avec modèle spectral JMA",
        key_variables=["T", "U", "V", "Q", "Z", "MSLP", "2T", "Precipitation"],
        references=["Kobayashi et al. (2015) J. Meteorol. Soc. Jpn. 93, 5-48"],
    ),
}


class ReanalysisEngine:
    """Moteur de recherche des réanalyses météorologiques mondiales."""

    @classmethod
    def get(cls, key: str) -> ReanalysisDatasetInfo | None:
        return REANALYSIS_REGISTRY.get(key.lower())

    @classmethod
    def list_datasets(cls) -> list[str]:
        return list(REANALYSIS_REGISTRY.keys())
