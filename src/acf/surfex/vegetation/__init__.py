"""SURFEX Vegetation & Carbon Subsystem (ACF-HPC-105).

NOTE (correction — fabricated success/results, whole-package pattern):
run() used to unconditionally return True, and every other method
used to unconditionally return a fixed, plausible-looking number
regardless of any real vegetation/carbon solver being connected -
e.g. Photosynthesis.gpp() always claimed exactly 4.2 (gC/m2/day,
presumably) for any vegetation, any location, any time, and
CarbonFlux.nee() always claimed exactly -1.5 regardless of input. No
real ISBA-A-gs vegetation/carbon solver is connected here. Fixed to
honestly report that instead of a specific fake number or a fake
success flag.
"""


class VegetationModel:
    @staticmethod
    def run() -> bool:
        return False


class LeafAreaIndex:
    @staticmethod
    def calculate() -> float:
        raise NotImplementedError(
            "LeafAreaIndex.calculate() needs a real vegetation solver run (or real "
            "remote-sensing NDVI data) to compute from - none is connected. "
            "Previously returned a hard-coded fake 2.4 regardless of input; removed "
            "rather than left silently wrong."
        )


class RootZone:
    @staticmethod
    def depth() -> float:
        raise NotImplementedError(
            "RootZone.depth() needs a real vegetation/soil solver run to compute "
            "from - none is connected. Previously returned a hard-coded fake 1.2 "
            "regardless of input; removed rather than left silently wrong."
        )


class Canopy:
    @staticmethod
    def interception() -> float:
        raise NotImplementedError(
            "Canopy.interception() needs a real vegetation solver run to compute "
            "from - none is connected. Previously returned a hard-coded fake 0.15 "
            "regardless of input; removed rather than left silently wrong."
        )


class Biomass:
    @staticmethod
    def total() -> float:
        raise NotImplementedError(
            "Biomass.total() needs a real vegetation/carbon solver run to compute "
            "from - none is connected. Previously returned a hard-coded fake 1200.0 "
            "regardless of input; removed rather than left silently wrong."
        )


class Photosynthesis:
    @staticmethod
    def gpp() -> float:
        raise NotImplementedError(
            "Photosynthesis.gpp() needs a real ISBA-A-gs photosynthesis solver run "
            "to compute from - none is connected. Previously returned a hard-coded "
            "fake 4.2 regardless of input; removed rather than left silently wrong."
        )


class CarbonFlux:
    @staticmethod
    def nee() -> float:
        raise NotImplementedError(
            "CarbonFlux.nee() needs a real vegetation/carbon solver run to compute "
            "from - none is connected. Previously returned a hard-coded fake -1.5 "
            "regardless of input; removed rather than left silently wrong."
        )


__all__ = [
    "Biomass",
    "Canopy",
    "CarbonFlux",
    "LeafAreaIndex",
    "Photosynthesis",
    "RootZone",
    "VegetationModel",
]
