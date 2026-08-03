"""
Atmospheric Complexity Framework (ACF)

Scientific Knowledge Sources & Literature Indexer Module
"""

from typing import Any, Dict, List


class KnowledgeSourcesIndexer:
    """
    Indexeur officiel et moteur de recherche dans les sources de la littérature scientifique
    (WMO, ECMWF, NOAA, NASA, ESA, DWD, Météo-France, ICAO, AMS, IPCC).
    """

    SOURCES_DATABASE: List[Dict[str, Any]] = [
        {"organization": "WMO", "code": "WMO-No. 8", "title": "Guide to Meteorological Instruments and Methods of Observation", "publication": "World Meteorological Organization Geneva", "author": "WMO Commission for Instruments", "year": "2018", "link": "https://library.wmo.int/doc_num.php?explnum_id=10616"},
        {"organization": "WMO", "code": "WMO-No. 407", "title": "International Cloud Atlas (Manual on the Observation of Clouds and Other Meteors)", "publication": "WMO Secretariat", "author": "WMO Cloud Committee", "year": "2017", "link": "https://wmocloudatlas.org"},
        {"organization": "WMO", "code": "WMO-No. 49", "title": "Technical Regulations - General Meteorological Standards", "publication": "WMO Geneva", "author": "WMO", "year": "2021", "link": "https://library.wmo.int"},
        {"organization": "WMO", "code": "WMO-No. 544", "title": "Manual on the Global Observing System", "publication": "WMO", "author": "WMO CBS", "year": "2019", "link": "https://library.wmo.int"},
        {"organization": "ECMWF", "code": "IFS Cy48r1", "title": "ECMWF Integrated Forecasting System Documentation (Part I-IV)", "publication": "ECMWF Reading UK", "author": "ECMWF Research Department", "year": "2023", "link": "https://www.ecmwf.int/en/publications/ifs-documentation"},
        {"organization": "ECMWF", "code": "ERA5 Tech Memo", "title": "ERA5 Reanalysis Global Atmosphere Specifications", "publication": "ECMWF", "author": "Hersbach et al.", "year": "2020", "link": "https://rmets.onlinelibrary.wiley.com/doi/10.1002/qj.3803"},
        {"organization": "NOAA", "code": "SPC Manual", "title": "NOAA Storm Prediction Center Severe Weather Forecasting Manual", "publication": "NOAA NWS Norman OK", "author": "NOAA SPC Meteorologists", "year": "2022", "link": "https://www.spc.noaa.gov/experience"},
        {"organization": "NOAA", "code": "NWS Directives", "title": "National Weather Service Radar and Convective Warning Standards", "publication": "NOAA NWS", "author": "NOAA Radar Operations Center", "year": "2021", "link": "https://www.weather.gov/directives"},
        {"organization": "NASA", "code": "MODIS ATBD", "title": "MODIS Algorithm Theoretical Basis Document for Cloud and Aerosol Products", "publication": "NASA Goddard Space Flight Center", "author": "King et al.", "year": "2015", "link": "https://modis.gsfc.nasa.gov/data/atbd"},
        {"organization": "NASA", "code": "VIIRS ATBD", "title": "VIIRS Atmosphere Products User Guide", "publication": "NASA / NOAA NESDIS", "author": "VIIRS Atmosphere Team", "year": "2020", "link": "https://visibleearth.nasa.gov"},
        {"organization": "ESA", "code": "Aeolus Mission", "title": "ESA Aeolus Doppler Wind Lidar Scientific Report", "publication": "European Space Agency", "author": "ESA Aeolus Science Team", "year": "2019", "link": "https://earth.esa.int/eogateway/missions/aeolus"},
        {"organization": "ESA", "code": "EarthCARE", "title": "ESA / JAXA EarthCARE Cloud & Aerosol Mission Handbook", "publication": "ESA Publications", "author": "ESA / JAXA EarthCARE Team", "year": "2024", "link": "https://earth.esa.int/eogateway/missions/earthcare"},
        {"organization": "ICAO", "code": "Annex 3", "title": "Meteorological Service for International Air Navigation Standards and Recommended Practices", "publication": "International Civil Aviation Organization Montreal", "author": "ICAO MET Panel", "year": "2021", "link": "https://www.icao.int"},
        {"organization": "AMS", "code": "AMS Glossary", "title": "Glossary of Meteorology (American Meteorological Society)", "publication": "AMS Boston MA", "author": "AMS Council", "year": "2024", "link": "https://glossary.ametsoc.org"},
        {"organization": "AMS", "code": "Mon. Wea. Rev.", "title": "Monthly Weather Review Scientific Journal Archive", "publication": "AMS", "author": "AMS Authors", "year": "2024", "link": "https://journals.ametsoc.org/view/journals/mwre/mwre-overview.xml"},
        {"organization": "IPCC", "code": "AR6 WG1", "title": "IPCC Sixth Assessment Report: The Physical Science Basis", "publication": "Cambridge University Press", "author": "IPCC Working Group I", "year": "2021", "link": "https://www.ipcc.ch/report/ar6/wg1"},
        {"organization": "DWD", "code": "ICON Manual", "title": "DWD ICON Model Documentation: Physics and Dynamics", "publication": "Deutscher Wetterdienst Offenbach", "author": "Zängl et al. (DWD / MPI-M)", "year": "2015", "link": "https://www.dwd.de/EN/research/weatherforecasting/num_modelling/01_num_weather_prediction_modells/icon_description.html"},
        {"organization": "Météo-France", "code": "AROME Documentation", "title": "Documentation Technique du Modèle AROME et du Schéma Microphysique ICE3/ICE4", "publication": "Météo-France Toulouse", "author": "Seity et al. / CNRM", "year": "2016", "link": "https://meteofrance.fr/recherche"},
    ]

    @classmethod
    def search_sources(cls, query: str) -> List[Dict[str, Any]]:
        """Recherche les références bibliographiques correspondant au mot-clé."""
        q = query.lower()
        res = []
        for s in cls.SOURCES_DATABASE:
            text = f"{s['organization']} {s['code']} {s['title']} {s.get('publication', '')}".lower()
            if q in text:
                res.append(s)
        return res

    @classmethod
    def list_sources(cls) -> List[Dict[str, Any]]:
        """Liste l'intégralité des sources bibliographiques enregistrées."""
        return cls.SOURCES_DATABASE
