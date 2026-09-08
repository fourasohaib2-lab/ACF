"""
Atmospheric Complexity Framework (ACF)

Health Monitor Engine Module (Phase 14)
(HealthMonitor, HealthReport supervising Modules, Services, Digital Twin, AEOS, AI, Forecast, Knowledge)
"""

import importlib
from dataclasses import dataclass


@dataclass
class HealthReport:
    """Rapport de santé globale du framework."""

    overall_health: str
    active_modules_count: int
    failed_services_count: int
    subsystem_statuses: dict[str, str]


class HealthMonitor:
    """
    Moniteur de santé globale supervisant tous les sous-systèmes d'ACF.
    """

    # Subsystem display name -> actual importable top-level package.
    SUBSYSTEM_MODULES = {
        "AEOS": "acf.aeos",
        "DigitalTwin": "acf.digital_twin",
        "EarthIntelligence": "acf.intelligence",
        "PlanetaryDefense": "acf.planetary",
        "Geoengineering": "acf.geoengineering",
        "ForecastEngine": "acf.forecast",
        "AI": "acf.ai",
    }
    SUBSYSTEMS = list(SUBSYSTEM_MODULES.keys())

    @classmethod
    def check_health(cls) -> HealthReport:
        """
        Effectue une vérification réelle (mais limitée) de la santé de
        tous les sous-systèmes : chaque sous-système est considéré
        "HEALTHY" si son package Python racine s'importe sans lever
        d'exception, "FAILED" sinon.

        NOTE (correction): this used to unconditionally report "100%
        HEALTHY" for all 7 subsystems with 0 failed services,
        regardless of their actual state - same fake-stub pattern as
        this session's other findings. A successful import is a real,
        if shallow, signal (it catches broken imports, syntax errors,
        missing dependencies) - not a full runtime/functional health
        check (which would need each subsystem to expose its own
        real self-test), but a genuine check rather than none.
        """
        statuses = {}
        failed_count = 0
        for name, module_path in cls.SUBSYSTEM_MODULES.items():
            try:
                importlib.import_module(module_path)
                statuses[name] = "HEALTHY / IMPORTABLE"
            except Exception as exc:
                statuses[name] = f"FAILED / IMPORT_ERROR: {exc}"
                failed_count += 1

        total = len(cls.SUBSYSTEM_MODULES)
        healthy_pct = 100.0 * (total - failed_count) / total if total else 0.0

        return HealthReport(
            overall_health=f"{healthy_pct:.0f}% HEALTHY ({total - failed_count}/{total} subsystems importable)",
            active_modules_count=total - failed_count,
            failed_services_count=failed_count,
            subsystem_statuses=statuses,
        )
