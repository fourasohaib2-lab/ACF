"""
Terrestrial Carbon Sink & NPP Model
"""

import math


class TerrestrialCarbonSink:
    """Modèle du puits de carbone terrestre et de la production primaire nette (NPP)."""

    @classmethod
    def net_primary_productivity_gtc_yr(cls, temp_c: float, precip_mm: float) -> float:
        """
        Estime la productivité primaire nette (NPP) locale via le modèle de Miami.

        NOTE (correction — Physics Guard): precip_mm was genuinely
        accepted but completely unused - the previous formula
        (55.0 * (1 - (1 + T/30)^-1)) matched neither the temperature-
        nor precipitation-limited terms of any established NPP model
        and would give identical output for a desert and a rainforest
        at the same temperature. Replaced with the Miami Model (Lieth
        1972, "Modeling the primary productivity of the world") - the
        standard textbook global terrestrial NPP model, applying
        Liebig's law of the minimum between a temperature-limited and
        a precipitation-limited estimate:
            NPP_T = 3000 / (1 + exp(1.315 - 0.119*T))   [g dry matter/m^2/yr, T in degC]
            NPP_P = 3000 * (1 - exp(-0.000664*P))        [g dry matter/m^2/yr, P in mm/yr]
            NPP = min(NPP_T, NPP_P)
        Converted to carbon mass using a standard ~0.45 dry-biomass
        carbon fraction. Despite the "_gtc_yr" name (kept unchanged to
        avoid breaking the existing import), this is a per-unit-area
        point estimate (g C/m^2/yr equivalent, not a global GtC/yr
        total) - a real global total would require integrating over
        vegetated land area, not available to this scalar function.
        """
        npp_temp_limited = 3000.0 / (1.0 + math.exp(1.315 - 0.119 * temp_c))
        npp_precip_limited = 3000.0 * (1.0 - math.exp(-0.000664 * precip_mm))
        npp_dry_matter_g_m2_yr = max(0.0, min(npp_temp_limited, npp_precip_limited))
        carbon_fraction = 0.45  # standard fraction of dry biomass mass that is carbon
        return npp_dry_matter_g_m2_yr * carbon_fraction
