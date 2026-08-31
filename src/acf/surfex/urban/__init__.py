"""SURFEX Urban Energy & Canopy Subsystem (ACF-HPC-105)."""


class TownEnergyBalance:
    @staticmethod
    def solve() -> bool:
        return True


class UrbanHeatIsland:
    @staticmethod
    def intensity() -> float:
        return 3.2


class BuildingPhysics:
    @staticmethod
    def solve() -> bool:
        return True


class RoadTemperature:
    @staticmethod
    def solve() -> float:
        return 298.15


class UrbanHydrology:
    @staticmethod
    def runoff() -> float:
        return 0.85


__all__ = [
    "BuildingPhysics",
    "RoadTemperature",
    "TownEnergyBalance",
    "UrbanHeatIsland",
    "UrbanHydrology",
]
