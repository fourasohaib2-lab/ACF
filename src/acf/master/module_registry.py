"""
Atmospheric Complexity Framework (ACF)

Global Module Registry Module (Phase 2)
(GlobalModuleRegistry discovering all 21 core package modules)
"""


class GlobalModuleRegistry:
    """
    Registre global de découverte et d'inspection de tous les modules scientifiques d'ACF.
    """

    MODULES: list[str] = [
        "Atmosphere",
        "Ocean",
        "Climate",
        "Hydrology",
        "Cryosphere",
        "SpaceWeather",
        "Geology",
        "Planetary",
        "Geoengineering",
        "DigitalTwin",
        "AEOS",
        "AI",
        "Science",
        "Visualization",
        "GUI",
        "Maps",
        "Forecast",
        "Knowledge",
        "Plugins",
        "Reports",
        "Operations",
    ]

    @classmethod
    def list_modules(cls) -> list[str]:
        return list(cls.MODULES)

    @classmethod
    def get_module_info(cls, name: str) -> dict[str, str] | None:
        """
        NOTE: 'status' reflects that the module NAME is a registered
        entry in this static catalog, not that its content has been
        scientifically verified (that claim was previously worded
        "ACTIVE / VERIFIED", which overstated what this lookup
        actually checks — a registry membership test, not an audit).
        """
        for mod in cls.MODULES:
            if mod.lower() == name.lower():
                return {
                    "name": mod,
                    "version": "41.0.0",
                    "author": "ACF Core Development Team",
                    "status": "REGISTERED",
                }
        return None
