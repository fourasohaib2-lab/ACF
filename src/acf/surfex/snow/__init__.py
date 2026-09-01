"""SURFEX Snow & Ice Modeling Subsystem (ACF-HPC-105).

NOTE (correction — fabricated success/results, whole-package pattern):
run()/assimilate()/predict() used to unconditionally return True, and
SnowDiagnostics.evaluate() used to unconditionally return a fixed
{"snow_depth_m": 0.45, "swe_mm": 120.0} - a plausible-looking snowpack
state fabricated regardless of any real physics being computed. No
real CROCUS/SNOWPACK solver or snow-course/satellite assimilation
feed is connected here. Fixed to honestly report that instead of a
specific fake number or a fake success flag.
"""


class CROCUS:
    """Detailed Snowpack Physics & Metamorphism Model."""

    @staticmethod
    def run() -> bool:
        return False


class SNOWPACK:
    """Multi-layer Snow & Avalanche Hazard Model."""

    @staticmethod
    def run() -> bool:
        return False


class SnowDiagnostics:
    @staticmethod
    def evaluate() -> dict:
        raise NotImplementedError(
            "SnowDiagnostics.evaluate() needs a real CROCUS/SNOWPACK solver run to "
            "diagnose from - none is connected. Previously returned a hard-coded "
            "fake snowpack state ({'snow_depth_m': 0.45, 'swe_mm': 120.0}); removed "
            "rather than left silently wrong."
        )


class SnowAssimilation:
    @staticmethod
    def assimilate() -> bool:
        return False


class SnowForecast:
    @staticmethod
    def predict() -> bool:
        return False


__all__ = ["CROCUS", "SNOWPACK", "SnowAssimilation", "SnowDiagnostics", "SnowForecast"]
