"""SURFEX Land Surface Models (ACF-HPC-105).

NOTE (correction — fabricated success, whole-package pattern): every
scheme here (and throughout surfex/ - engine.py already honestly
disclosed no real HPC scheduler is connected, but this scaffolding
around it did not) used to unconditionally return True from run(),
regardless of any real dynamic-core solver being connected. Calling
ISBA.run() or TEB.run() looked exactly like a successful land-surface
simulation completing, for a scheme that does not exist here. Fixed
to honestly return False (no real solver connected), matching the
"no fabricated success" convention already used in
acf.models.base_model.BaseWeatherModel.stop()/resume().
"""


class ISBA:
    """Interaction between Soil, Biosphere, and Atmosphere scheme."""

    @staticmethod
    def run() -> bool:
        return False


class TEB:
    """Town Energy Balance urban canopy scheme."""

    @staticmethod
    def run() -> bool:
        return False


class SEA:
    """Sea Surface Energy & Flux Scheme."""

    @staticmethod
    def run() -> bool:
        return False


class LAKE:
    """FLAKE Lake Thermal & Energy Scheme."""

    @staticmethod
    def run() -> bool:
        return False


class RIVER:
    """River Routing & Hydrology Scheme."""

    @staticmethod
    def run() -> bool:
        return False


class COAST:
    """Coastal Zone Interactions Scheme."""

    @staticmethod
    def run() -> bool:
        return False


__all__ = ["COAST", "ISBA", "LAKE", "RIVER", "SEA", "TEB"]
