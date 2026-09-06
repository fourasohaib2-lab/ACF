"""
Atmospheric Complexity Framework (ACF)

AEOS Service Registry Module (Phase 2)
(ServiceRegistry registering Atmosphere, Ocean, Hydrology, Climate, Geology, Space Weather, Digital Twin, AI)
"""


class ServiceRegistry:
    """
    Registre centralisé de tous les microservices scientifiques du système d'exploitation AEOS.

    NOTE (Physics Guard, 2026-09-06 Tier E sweep): despite "Registre" /
    get_service_info()'s "status": "REGISTERED", no actual service
    object is ever instantiated or registered here - SERVICES is a
    fixed class-level list of names, and get_service_info() only
    checks membership in that list, then reports "REGISTERED"
    regardless of whether anything real backs that name (none of the
    15 listed *Service classes exist anywhere in this codebase,
    verified by grep). Real, deterministic list lookup, not a
    fabricated numeric result, but "REGISTERED" here means "the name
    is in a static list", not "a service was actually started".
    """

    SERVICES: list[str] = [
        "AtmosphereService",
        "OceanographyService",
        "HydrologyService",
        "CryosphereService",
        "ClimateService",
        "GeologySeismologyService",
        "SpaceWeatherService",
        "DigitalTwinService",
        "KnowledgeGraphService",
        "ArtificialIntelligenceService",
        "ForecastService",
        "ReportsGeneratorService",
        "VisualizationService",
        "MissionPlannerService",
        "DecisionSupportService",
    ]

    @classmethod
    def list_registered_services(cls) -> list[str]:
        return list(cls.SERVICES)

    @classmethod
    def get_service_info(cls, name: str) -> dict[str, str] | None:
        if name in cls.SERVICES:
            return {"name": name, "status": "REGISTERED", "domain": name.replace("Service", "")}
        return None
