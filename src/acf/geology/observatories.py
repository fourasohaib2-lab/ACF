"""
Atmospheric Complexity Framework (ACF)

Global Geological Observatories & Seismological Data Center Registry Module (Phase 15)
(USGS, EMSC, GFZ)

NOTE (correction — registry/docstring overclaim, found during the
post-model4d audit, 2026-09-06): this header used to also list "IRIS",
"ISC", "INGV", "BRGM", "NOAA", "UNESCO IOC" and "JMA" - 7 real
seismological/geological agencies that GEOLOGICAL_OBSERVATORIES_REGISTRY
below never had entries for (only usgs, emsc and gfz are populated).
get_observatory("iris")/("jma")/etc. silently returned None for any of
the 7 falsely-advertised agencies. Corrected to name only what is
genuinely in the registry, matching the docstring-vs-registry fix
already applied elsewhere in this audit (geoengineering/aviation/
hydrology), rather than inventing new GeologicalObservatoryInfo
entries with unverified API URLs/references.
"""

from dataclasses import dataclass


@dataclass
class GeologicalObservatoryInfo:
    """Description scientifique d'un observatoire sismologique ou géologique international."""

    key: str
    name: str
    agency: str
    location: str
    datasets_provided: list[str]
    api_url: str
    references: list[str]


GEOLOGICAL_OBSERVATORIES_REGISTRY: dict[str, GeologicalObservatoryInfo] = {
    "usgs": GeologicalObservatoryInfo(
        key="usgs",
        name="USGS Earthquake Hazards Program",
        agency="United States Geological Survey (USGS)",
        location="Reston, VA, USA",
        datasets_provided=["Real-time Earthquake Feeds (GeoJSON)", "ShakeMap (PGA/PGV)", "PAGER Loss Estimates"],
        api_url="https://earthquake.usgs.gov/fdsnws/event/1/",
        references=["USGS Earthquake Hazards Manual"],
    ),
    "emsc": GeologicalObservatoryInfo(
        key="emsc",
        name="EMSC (European-Mediterranean Seismological Centre)",
        agency="EMSC / Euro-Med Consortium",
        location="Bruyères-le-Châtel, France",
        datasets_provided=["Real-time Mediterranean & Global Seismicity", "Witness Macroseismic Reports"],
        api_url="https://www.seismicportal.eu/fdsnws/event/1/",
        references=["EMSC Real-time Seismicity Charter"],
    ),
    "gfz": GeologicalObservatoryInfo(
        key="gfz",
        name="GFZ German Research Centre for Geosciences",
        agency="Helmholtz Centre Potsdam (GFZ)",
        location="Potsdam, Germany",
        datasets_provided=["GEOFON Global Seismic Network", "GOCE/GRACE Gravity Datasets", "InSAR Displacement"],
        api_url="https://geofon.gfz-potsdam.de/fdsnws/event/1/",
        references=["GEOFON Program Overview"],
    ),
}


class GeologicalObservatoryEngine:
    """Moteur de consultation des observatoires et centres de données sismologiques."""

    @classmethod
    def get_observatory(cls, key: str) -> GeologicalObservatoryInfo | None:
        return GEOLOGICAL_OBSERVATORIES_REGISTRY.get(key.lower())

    @classmethod
    def list_observatories(cls) -> list[str]:
        return list(GEOLOGICAL_OBSERVATORIES_REGISTRY.keys())
