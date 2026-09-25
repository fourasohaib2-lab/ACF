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
    LayerSpec("icing_potential", "Icing potential", "0/1", True,
              "-20 <= T <= 0 degC and RH over water >= 70 % (RH from q, T, p; IFS r is not used: it is w.r.t. ice below -23 degC)",
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
    # --- SP1C clouds (model diagnostics, never observations) ---
    LayerSpec("surface_height_m", "IFS model surface height used for heights above ground", "m AMSL", False,
              "z_s = gh_k - (Rd Tv_mean / g) ln(p_s / p_k), k = lowest level above ground",
              "hypsometric equation; ECMWF IFS sp, 2t, 2d, gh, t, q", "CONFIRMED"),
    LayerSpec("cloud_fraction", "Level cloud fraction (diagnosed)", "0-1", True,
              "C = 1 - sqrt((1 - RH) / (1 - RHc)) for RH >= RHc, RH = IFS r (mixed phase), RHc per etage",
              "Sundqvist, Berge & Kristjansson (1989), Mon. Wea. Rev. 117; RHc in cloud profile", "HYPOTHESIS"),
    LayerSpec("cloud_genus", "Probable cloud genus of the layer (model diagnostic)", "WMO code 0500, -1 clear, -2 indeterminate",
              True, "rule table SP1C spec 3.9 (etage, depth, cover, dtheta_e/dz, precipitation, convection)",
              "WMO-No. 407 genera; thresholds in cloud profile", "HYPOTHESIS"),
    LayerSpec("potential_instability", "Potential instability dtheta_e/dz", "K/km", True,
              "(theta_e(k+1) - theta_e(k)) / (gh(k+1) - gh(k)); < 0 = potentially unstable",
              "AMS Glossary (potential instability); Bolton (1980) theta_e", "CONFIRMED"),
    LayerSpec("cloud_cover_low", "Low cloud cover (sigma > 0.8)", "0-1", False, "maximum-random overlap over the etage",
              "Geleyn & Hollingsworth (1979); ECMWF etage bounds", "HYPOTHESIS"),
    LayerSpec("cloud_cover_mid", "Medium cloud cover (0.45 < sigma <= 0.8)", "0-1", False,
              "maximum-random overlap over the etage", "Geleyn & Hollingsworth (1979); ECMWF etage bounds", "HYPOTHESIS"),
    LayerSpec("cloud_cover_high", "High cloud cover (sigma <= 0.45)", "0-1", False, "maximum-random overlap over the etage",
              "Geleyn & Hollingsworth (1979); ECMWF etage bounds", "HYPOTHESIS"),
    LayerSpec("cloud_cover_total_diag", "Total cloud cover (diagnosed)", "0-1", False,
              "1 - prod (1 - max(C_k, C_k-1)) / (1 - C_k-1)", "Geleyn & Hollingsworth (1979), Raisanen (1998)", "HYPOTHESIS"),
    LayerSpec("tcc", "Total cloud cover (IFS)", "0-1", False, "IFS field", "ECMWF IFS", "CONFIRMED"),
    LayerSpec("cloud_cover_bias", "Diagnosed minus IFS total cloud cover", "-1..1", False,
              "cloud_cover_total_diag - tcc (consistency check)", "ACF", "CONFIRMED"),
    LayerSpec("ceiling_m", "Ceiling (ICAO definition)", "m AGL", False,
              "base of the lowest diagnosed layer below 6000 m with BKN/OVC; convective layers excluded (cover unknown)",
              "ICAO Annex 2 definition of ceiling", "HYPOTHESIS"),
    LayerSpec("lowest_cloud_base_m", "Lowest cloud base", "m AGL", False,
              "min(base of diagnosed layers, LCL of convection)", "ACF", "HYPOTHESIS"),
    LayerSpec("highest_cloud_top_m", "Highest cloud top", "m AMSL", False,
              "max(top gh of diagnosed layers, convective top)", "ACF", "HYPOTHESIS"),
    LayerSpec("genus_low", "Dominant probable genus, low etage", "WMO code 0500", False,
              "genus of the largest-cover layer based in the etage; Cb/TCU take precedence", "ACF", "HYPOTHESIS"),
    LayerSpec("genus_mid", "Dominant probable genus, medium etage", "WMO code 0500", False,
              "genus of the largest-cover layer based in the etage; Cb/TCU take precedence", "ACF", "HYPOTHESIS"),
    LayerSpec("genus_high", "Dominant probable genus, high etage", "WMO code 0500", False,
              "genus of the largest-cover layer based in the etage", "ACF", "HYPOTHESIS"),
    LayerSpec("convective_class", "Convective cloud class", "0 none, 1 Cu hum/med, 2 TCU, 3 Cb calvus, 4 Cb capillatus",
              False, "surface parcel EL depth + mucape + top temperature + precipitation (cloud profile)",
              "Bolton (1980) parcel; Rosenfeld & Lensky (1998); Pruppacher & Klett (1997)", "HYPOTHESIS"),
    LayerSpec("convective_top_m", "Convective cloud top (parcel EL)", "m AMSL", False,
              "gh of the highest level where Tv_parcel > Tv_env", "Bolton (1980) pseudo-adiabat", "HYPOTHESIS"),
    LayerSpec("convective_top_temp_k", "Convective top temperature", "K", False, "T_env at the EL",
              "Bolton (1980) pseudo-adiabat", "HYPOTHESIS"),
    LayerSpec("species_flags", "Diagnosable cloud species", "bits: 1 cas, 2 len, 4 fra, 8 neb, 16 spi", False,
              "rule table SP1C spec 3.10", "WMO-No. 407 species; Durran (1990) mountain waves", "HYPOTHESIS"),
    LayerSpec("cloud_top_teff_k", "Effective emission temperature (from OLR)", "K", False,
              "(OLR / sigma)^(1/4), OLR = -d(ttr)/dt, broadband", "ECMWF ttr; Stefan-Boltzmann (CODATA 2018)", "CONFIRMED"),
    LayerSpec("column_condensate", "Column condensate (cloud liquid + ice + rain + snow)", "kg/m^2", False,
              "tcw - tcwv", "ECMWF IFS", "CONFIRMED"),
    LayerSpec("snowfall_mm", "Snowfall over the preceding interval", "mm water equivalent", False,
              "(sf(t) - sf(t - dt)) x 1000", "ECMWF IFS", "CONFIRMED"),
    LayerSpec("snow_depth_cm", "Snow depth", "cm", False, "sd x 1000 / rsn x 100", "ECMWF IFS", "CONFIRMED"),
    LayerSpec("freezing_precip_mm", "Freezing precipitation over the preceding interval (not an ice thickness)", "mm",
              False, "tp increment when ptype in {3, 12} at both ends", "ECMWF IFS ptype codes", "HYPOTHESIS"),
)

LAYERS: dict[str, LayerSpec] = {spec.name: spec for spec in _SPECS}

#: Stored cube variables (names only - kept here, free of eccodes/netCDF imports, so the web router
#: can be imported with the ``web`` extra alone).
MODULES: tuple[str, ...] = ("dynamic", "thermodynamic", "convective", "microphysical", "topographic")
LEVEL_LAYERS: tuple[str, ...] = (
    "t", "q", "r", "u", "v", "w", "gh", "wind_speed", "layer_shear", "vertical_shear", "cat_ti2",
    "cat_category", "icing_potential", "theta_e", "awci", "awci_level", *(f"module_{m}" for m in MODULES),
    "cloud_fraction", "cloud_genus", "potential_instability",
)
SURFACE_LAYERS: tuple[str, ...] = (
    "t2m", "d2m", "rh2m", "mucape", "cloud_base_lcl", "precip_rate", "precip_class", "precip_type",
    "ptype_severity", "gust_10m", "dust_proxy", "tcc", "sp_hpa",
    "cloud_cover_low", "cloud_cover_mid", "cloud_cover_high", "cloud_cover_total_diag", "ceiling_m",
    "lowest_cloud_base_m", "highest_cloud_top_m", "genus_low", "genus_mid", "genus_high", "convective_class",
    "convective_top_m", "convective_top_temp_k", "species_flags",
    "cloud_cover_bias", "cloud_top_teff_k", "column_condensate", "snowfall_mm", "snow_depth_cm", "freezing_precip_mm",
    "surface_height_m",
)
