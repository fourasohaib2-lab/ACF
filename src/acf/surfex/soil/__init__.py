"""SURFEX Soil Physics & Hydrology Subsystem (ACF-HPC-105).

NOTE (correction — fabricated success/results, whole-package pattern):
run()/solve() used to unconditionally return True, and
evaluate()/rate()/surface()/recharge() used to unconditionally return
a fixed, plausible-looking number regardless of any real soil physics
solver being connected - e.g. SoilMoisture.evaluate() always claimed
exactly 0.28 (volumetric fraction, presumably) for any soil, any
location, any time. No real ISBA soil solver is connected here. Fixed
to honestly report that instead of a specific fake number or a fake
success flag.
"""


class SoilHydrology:
    @staticmethod
    def solve() -> bool:
        return False


class SoilTemperature:
    @staticmethod
    def solve() -> bool:
        return False


class SoilMoisture:
    @staticmethod
    def evaluate() -> float:
        raise NotImplementedError(
            "SoilMoisture.evaluate() needs a real soil physics solver run to "
            "compute from - none is connected. Previously returned a hard-coded "
            "fake 0.28 regardless of input; removed rather than left silently wrong."
        )


class Drainage:
    @staticmethod
    def rate() -> float:
        raise NotImplementedError(
            "Drainage.rate() needs a real soil physics solver run to compute from - "
            "none is connected. Previously returned a hard-coded fake 0.02 regardless "
            "of input; removed rather than left silently wrong."
        )


class Runoff:
    @staticmethod
    def surface() -> float:
        raise NotImplementedError(
            "Runoff.surface() needs a real soil physics solver run to compute from - "
            "none is connected. Previously returned a hard-coded fake 0.05 regardless "
            "of input; removed rather than left silently wrong."
        )


class Groundwater:
    @staticmethod
    def recharge() -> float:
        raise NotImplementedError(
            "Groundwater.recharge() needs a real soil physics solver run to compute "
            "from - none is connected. Previously returned a hard-coded fake 0.01 "
            "regardless of input; removed rather than left silently wrong."
        )


__all__ = [
    "Drainage",
    "Groundwater",
    "Runoff",
    "SoilHydrology",
    "SoilMoisture",
    "SoilTemperature",
]
