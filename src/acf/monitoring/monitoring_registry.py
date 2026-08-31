"""
Atmospheric Complexity Framework (ACF)

Global Monitoring Registry Module (Phase 9)
(MonitoringRegistry cataloguing all monitored services, sensors, and agents)
"""

from typing import Any


class MonitoringRegistry:
    """
    Registre d'inventaire et d'état de tous les services, capteurs et agents de surveillance.
    """

    MONITORED_SERVICES = [
        "AEOSKernelService",
        "DigitalTwinSyncService",
        "EarthIntelligenceService",
        "PlanetaryDefenseService",
        "GeoengineeringService",
        "ObservationStreamService",
        "WebSocketBroadcastService",
        "AlertDispatcherService",
    ]

    @classmethod
    def get_registry_status(cls) -> dict[str, Any]:
        """
        Retourne l'état du registre d'inventaire de la surveillance.

        NOTE (correction): MONITORED_SERVICES is a genuine static
        catalog of the intended service names, but this used to also
        claim a fabricated "18500 sensors" / "12 active agents" count
        and "ALL_REGISTERED_SERVICES_HEALTHY" - no real
        sensor/agent inventory or per-service health check is
        connected here. Not fabricated.
        """
        return {
            "monitored_services_count": len(cls.MONITORED_SERVICES),
            "services": cls.MONITORED_SERVICES,
            "monitored_sensors_count": None,
            "monitoring_agents_active": None,
            "registry_health": "NOT_CHECKED_NO_HEALTH_PROBE_CONNECTED",
            "is_real_data": False,
        }
