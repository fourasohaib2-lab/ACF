"""SURFEX Land Surface Models (ACF-HPC-105)."""


class ISBA:
    """Interaction between Soil, Biosphere, and Atmosphere scheme."""

    @staticmethod
    def run() -> bool:
        return True


class TEB:
    """Town Energy Balance urban canopy scheme."""

    @staticmethod
    def run() -> bool:
        return True


class SEA:
    """Sea Surface Energy & Flux Scheme."""

    @staticmethod
    def run() -> bool:
        return True


class LAKE:
    """FLAKE Lake Thermal & Energy Scheme."""

    @staticmethod
    def run() -> bool:
        return True


class RIVER:
    """River Routing & Hydrology Scheme."""

    @staticmethod
    def run() -> bool:
        return True


class COAST:
    """Coastal Zone Interactions Scheme."""

    @staticmethod
    def run() -> bool:
        return True


__all__ = ["COAST", "ISBA", "LAKE", "RIVER", "SEA", "TEB"]
