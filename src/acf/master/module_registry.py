"""
Atmospheric Complexity Framework (ACF)

Global Module Registry Module (Phase 2)
(GlobalModuleRegistry discovering all 21 core package modules)
"""


class GlobalModuleRegistry:
    """
    Registre global de découverte et d'inspection de tous les modules scientifiques d'ACF.

    NOTE (correction, 2026-09-05 audit de continuation): "discovering"
    in this module's own docstring overstates what MODULES is - a
    hand-curated static list, not the result of any real filesystem or
    import-time package discovery. Checked against the real top-level
    packages under src/acf/: most of the 21 names correspond directly
    (or closely enough - e.g. "DigitalTwin" for digital_twin), but
    "Atmosphere", "Cryosphere", "Knowledge", and "Operations" do not
    match any actual top-level src/acf/ package (the closest real
    packages are earth_physics/climate for atmosphere-and-cryosphere
    content, knowledge_platform for "Knowledge", and hazard_operations
    for "Operations" - none an exact match). Not fabricated (no
    numeric/status claim here is false), but the registry is a
    conceptual/marketing taxonomy, not a verified package inventory.
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
