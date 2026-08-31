"""SURFEX Vegetation & Carbon Subsystem (ACF-HPC-105)."""


class VegetationModel:
    @staticmethod
    def run() -> bool:
        return True


class LeafAreaIndex:
    @staticmethod
    def calculate() -> float:
        return 2.4


class RootZone:
    @staticmethod
    def depth() -> float:
        return 1.2


class Canopy:
    @staticmethod
    def interception() -> float:
        return 0.15


class Biomass:
    @staticmethod
    def total() -> float:
        return 1200.0


class Photosynthesis:
    @staticmethod
    def gpp() -> float:
        return 4.2


class CarbonFlux:
    @staticmethod
    def nee() -> float:
        return -1.5


__all__ = [
    "Biomass",
    "Canopy",
    "CarbonFlux",
    "LeafAreaIndex",
    "Photosynthesis",
    "RootZone",
    "VegetationModel",
]
