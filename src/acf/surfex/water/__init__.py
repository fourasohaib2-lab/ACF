"""SURFEX Water & Inland Body Subsystem (ACF-HPC-105)."""


class Evaporation:
    @staticmethod
    def solve() -> float:
        return 2.5


class Evapotranspiration:
    @staticmethod
    def solve() -> float:
        return 3.1


class SurfaceFluxes:
    @staticmethod
    def compute() -> dict:
        return {"latent": 120.0, "sensible": 45.0}


class RiverRouting:
    @staticmethod
    def route() -> bool:
        return True


class LakeModel:
    @staticmethod
    def solve() -> bool:
        return True


__all__ = [
    "Evaporation",
    "Evapotranspiration",
    "LakeModel",
    "RiverRouting",
    "SurfaceFluxes",
]
