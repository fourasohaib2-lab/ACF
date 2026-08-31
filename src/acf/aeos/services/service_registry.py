"""
Atmospheric Complexity Framework (ACF)

AEOS Service Registry Module (Phase 2)
(ServiceRegistry registering Atmosphere, Ocean, Hydrology, Climate, Geology, Space Weather, Digital Twin, AI)
"""


class ServiceRegistry:
    """
    Registre centralisé de tous les microservices scientifiques du système d'exploitation AEOS.
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
