"""Single source of truth for every layer served by /api/v1/awci (unit, equation, source, status)."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class LayerSpec:
    name: str
    label: str
    unit: str
    per_level: bool
    equation: str
    source: str
    status: str  # ScientificStatus value from acf.awci.scientific_status

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


_SPECS = (
    LayerSpec("wind_speed", "Wind speed", "m/s", True, "sqrt(u^2 + v^2)", "IFS u, v", "CONFIRMED"),
    LayerSpec("layer_shear", "Layer wind shear", "m/s", True, "|V(k+1) - V(k)|", "IFS u, v", "CONFIRMED"),
    LayerSpec("vertical_shear", "Vertical wind shear", "1/s", True, "|dV| / dgh", "IFS u, v, gh", "CONFIRMED"),
    LayerSpec("cat_ti2", "Clear-air turbulence (Ellrod TI2)", "1/s^2", True, "VWS * (DEF - div)",
              "Ellrod & Knapp (1992), Wea. Forecasting 7, 150-165", "HYPOTHESIS"),
    LayerSpec("cat_category", "CAT category", "code 0-3", True, "TI2 x1e7 thresholds 4/8/12",
              "Ellrod & Knapp (1992)", "HYPOTHESIS"),
    LayerSpec("icing_potential", "Icing potential", "0/1", True, "-20 <= T <= 0 degC and RH >= 70 %",
              "T+RH approach of Schultz & Politovich (1992); thresholds ACF choice", "HYPOTHESIS"),
    LayerSpec("theta_e", "Equivalent potential temperature", "K", True, "Bolton (1980) eq. 43",
              "Bolton (1980), Mon. Wea. Rev. 108, 1046-1053", "CONFIRMED"),
    LayerSpec("mucape", "Most-unstable CAPE", "J/kg", False, "IFS field", "ECMWF IFS", "CONFIRMED"),
    LayerSpec("cloud_base_lcl", "Estimated cloud base (LCL) - not a ceiling", "m AGL", False,
              "125 m x (T2m - Td2m)", "Espy approximation", "HYPOTHESIS"),
    LayerSpec("precip_rate", "Precipitation rate", "mm/h", False, "tprate x 3600", "ECMWF IFS", "CONFIRMED"),
    LayerSpec("precip_class", "Precipitation intensity", "code 0-4", False, "WMO bounds 2.5/10/50 mm/h",
              "WMO-No. 8", "CONFIRMED"),
    LayerSpec("precip_type", "Precipitation type", "ECMWF code", False, "IFS ptype", "ECMWF IFS", "CONFIRMED"),
    LayerSpec("gust_10m", "10 m wind gust", "m/s", False, "IFS 10fg", "ECMWF IFS", "CONFIRMED"),
    LayerSpec("dust_proxy", "Dust-raising proxy (not a concentration)", "0-1", False,
              "ramp(gust, 8, 18) x (1 - ramp(RH2m, 20, 70))", "ACF proxy", "HYPOTHESIS"),
    LayerSpec("awci", "AWCI (operational-v1)", "0-100", True, "weighted modules, missing ones renormalized",
              "ACF composite index", "HYPOTHESIS"),
)

LAYERS: dict[str, LayerSpec] = {spec.name: spec for spec in _SPECS}
