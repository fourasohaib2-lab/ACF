"""
Scientific Knowledge Sources & Literature Indexer Module
"""

from typing import Any, Dict, List


class KnowledgeSourcesIndexer:
    """
    Indexeur officiel des répertoriations de la littérature scientifique (WMO, ECMWF, NOAA, NASA, ICAO, AMS).
    """

    SOURCES_DATABASE = [
        {"organization": "WMO", "code": "WMO-No. 8", "title": "Guide to Meteorological Instruments and Methods of Observation"},
        {"organization": "WMO", "code": "WMO-No. 407", "title": "International Cloud Atlas"},
        {"organization": "ECMWF", "code": "IFS Cy48r1", "title": "ECMWF Integrated Forecasting System Documentation"},
        {"organization": "NOAA", "code": "SPC Manual", "title": "Severe Weather Forecasting Manual"},
        {"organization": "ICAO", "code": "Annex 3", "title": "Meteorological Service for International Air Navigation"},
        {"organization": "AMS", "code": "AMS Glossary", "title": "Glossary of Meteorology (American Meteorological Society)"},
        {"organization": "IPCC", "code": "AR6 WG1", "title": "The Physical Science Basis"},
    ]

    @classmethod
    def search_sources(cls, query: str) -> List[Dict[str, Any]]:
        q = query.lower()
        res = []
        for s in cls.SOURCES_DATABASE:
            text = f"{s['organization']} {s['code']} {s['title']}".lower()
            if q in text:
                res.append(s)
        return res

    @classmethod
    def list_sources(cls) -> List[Dict[str, Any]]:
        return cls.SOURCES_DATABASE
