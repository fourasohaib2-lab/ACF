"""SURFEX Water & Inland Body Subsystem (ACF-HPC-105).

NOTE (correction — fabricated results, whole-package pattern): every
method here used to unconditionally return a fixed, plausible-looking
number (or True) regardless of any real hydrology solver being
connected - e.g. Evaporation.solve() always claimed exactly 2.5
(mm/day, presumably) for any location or weather. No real water-body
physics solver is connected here. Fixed to honestly report that
instead of a specific fake number.
"""


class Evaporation:
    @staticmethod
    def solve() -> float:
        raise NotImplementedError(
            "Evaporation.solve() needs a real water-body energy balance solver run "
            "to compute from - none is connected. Previously returned a hard-coded "
            "fake 2.5 regardless of input; removed rather than left silently wrong."
        )


class Evapotranspiration:
    @staticmethod
    def solve() -> float:
        raise NotImplementedError(
            "Evapotranspiration.solve() needs a real land-surface energy balance "
            "solver run to compute from - none is connected. Previously returned a "
            "hard-coded fake 3.1 regardless of input; removed rather than left "
            "silently wrong."
        )


class SurfaceFluxes:
    @staticmethod
    def compute() -> dict:
        raise NotImplementedError(
            "SurfaceFluxes.compute() needs a real energy balance solver run to "
            "compute from - none is connected. Previously returned a hard-coded fake "
            "{'latent': 120.0, 'sensible': 45.0} regardless of input; removed rather "
            "than left silently wrong."
        )


class RiverRouting:
    @staticmethod
    def route() -> bool:
        return False


class LakeModel:
    @staticmethod
    def solve() -> bool:
        return False


__all__ = [
    "Evaporation",
    "Evapotranspiration",
    "LakeModel",
    "RiverRouting",
    "SurfaceFluxes",
]
