"""SURFEX Soil Physics & Hydrology Subsystem (ACF-HPC-105)."""


class SoilHydrology:
    @staticmethod
    def solve() -> bool:
        return True


class SoilTemperature:
    @staticmethod
    def solve() -> bool:
        return True


class SoilMoisture:
    @staticmethod
    def evaluate() -> float:
        return 0.28


class Drainage:
    @staticmethod
    def rate() -> float:
        return 0.02


class Runoff:
    @staticmethod
    def surface() -> float:
        return 0.05


class Groundwater:
    @staticmethod
    def recharge() -> float:
        return 0.01


__all__ = [
    "Drainage",
    "Groundwater",
    "Runoff",
    "SoilHydrology",
    "SoilMoisture",
    "SoilTemperature",
]
