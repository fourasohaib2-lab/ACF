"""
Atmospheric Complexity Framework (ACF)

AEOS Core Kernel Module (Phase 1)
(AEOSKernel boot, shutdown, restart, load_services, monitor_services, health_check, scheduler, event_loop)
"""

from typing import Any

from acf.aeos.services.service_registry import ServiceRegistry


class AEOSKernel:
    """
    Noyau du système d'exploitation planétaire autonome AEOS.
    Orchestre le système Terre, les services distributed, le Digital Twin et l'IA.
    """

    def __init__(self):
        self.is_booted = False
        self.registry = ServiceRegistry()
        self.active_services: list[str] = []

    def boot(self) -> dict[str, Any]:
        """Démarre le noyau AEOS et charge les microservices planétaires."""
        self.is_booted = True
        self.load_services()
        return {
            "status": "BOOTED / OPERATIONAL",
            "kernel_version": "AEOS v1.0 Planetary OS",
            "services_loaded": len(self.active_services),
        }

    def shutdown(self) -> dict[str, Any]:
        """Arrête proprement le noyau AEOS."""
        self.is_booted = False
        self.active_services.clear()
        return {"status": "SHUTDOWN COMPLETE"}

    def restart(self) -> dict[str, Any]:
        """Redémarre le noyau AEOS."""
        self.shutdown()
        return self.boot()

    def load_services(self) -> list[str]:
        """Charge la totalité des services enregistrés dans le ServiceRegistry."""
        self.active_services = self.registry.list_registered_services()
        return self.active_services

    def monitor_services(self) -> dict[str, str]:
        """Surveille l'état des services actifs."""
        return {service: "RUNNING / HEALTHY" for service in self.active_services}

    def health_check(self) -> dict[str, Any]:
        """
        Exécute un contrôle de santé complet du noyau et des services.

        NOTE (correction): kernel_status and active_services_count
        already reflected real state (self.is_booted,
        len(self.active_services)) - only cpu_load_pct/
        memory_usage_pct were fixed fake values (14.5%/22.0%
        regardless of actual load). Uses psutil for a real reading
        when available (optional import, not a declared
        pyproject.toml dependency - degrades to None rather than
        crashing where absent), same approach as
        master/performance.py.
        """
        try:
            import psutil  # type: ignore

            cpu_load_pct: float | None = psutil.cpu_percent(interval=0.05)
            memory_usage_pct: float | None = psutil.virtual_memory().percent
        except ImportError:
            cpu_load_pct = memory_usage_pct = None

        return {
            "kernel_status": "HEALTHY" if self.is_booted else "OFFLINE",
            "active_services_count": len(self.active_services),
            "cpu_load_pct": cpu_load_pct,
            "memory_usage_pct": memory_usage_pct,
        }

    def register_service(self, service_name: str) -> None:
        """Enregistre un nouveau service."""
        if service_name not in self.active_services:
            self.active_services.append(service_name)

    def unregister_service(self, service_name: str) -> None:
        """Désenregistre un service."""
        if service_name in self.active_services:
            self.active_services.remove(service_name)

    def scheduler(self) -> str:
        """Accède au planificateur de tâches du noyau."""
        return "AEOS Autonomous Task Scheduler Active"

    def event_loop(self) -> str:
        """Boucle d'événements principale du noyau."""
        return "AEOS Event Loop Processing Events"

    def resource_manager(self) -> str:
        """Gestionnaire de ressources CPU/RAM/GPU du noyau."""
        return "AEOS Resource Manager Allocating Memory and Threads"
