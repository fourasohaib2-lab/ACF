"""SURFEX Urban Energy & Canopy Subsystem (ACF-HPC-105).

NOTE (correction — fabricated results, whole-package pattern): every
method here used to unconditionally return a fixed, plausible-looking
number (or True) regardless of any real Town Energy Balance solver
being connected - e.g. UrbanHeatIsland.intensity() always claimed
3.2 K of urban heat island intensity, RoadTemperature.solve() always
claimed exactly 298.15 K, for any city, any time, any weather. No
real TEB solver is connected here. Fixed to honestly report that
instead of a specific fake number.
"""


class TownEnergyBalance:
    @staticmethod
    def solve() -> bool:
        return False


class UrbanHeatIsland:
    @staticmethod
    def intensity() -> float:
        raise NotImplementedError(
            "UrbanHeatIsland.intensity() needs a real Town Energy Balance solver run "
            "to diagnose from - none is connected. Previously returned a hard-coded "
            "fake 3.2 K regardless of city or conditions; removed rather than left "
            "silently wrong."
        )


class BuildingPhysics:
    @staticmethod
    def solve() -> bool:
        return False


class RoadTemperature:
    @staticmethod
    def solve() -> float:
        raise NotImplementedError(
            "RoadTemperature.solve() needs a real Town Energy Balance solver run to "
            "compute from - none is connected. Previously returned a hard-coded fake "
            "298.15 K regardless of conditions; removed rather than left silently wrong."
        )


class UrbanHydrology:
    @staticmethod
    def runoff() -> float:
        raise NotImplementedError(
            "UrbanHydrology.runoff() needs real precipitation and surface data to "
            "compute from - none is connected. Previously returned a hard-coded fake "
            "0.85 regardless of input; removed rather than left silently wrong."
        )


__all__ = [
    "BuildingPhysics",
    "RoadTemperature",
    "TownEnergyBalance",
    "UrbanHeatIsland",
    "UrbanHydrology",
]
