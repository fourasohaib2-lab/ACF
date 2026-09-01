"""
Sea Ice Thermodynamics Model (Growth & Melt)
"""


class SeaIceThermodynamics:
    """Modèle thermodynamique de croissance et de fonte de la banquise (Stefan Growth Rule)."""

    #: Thermal conductivity of sea ice, W/(m*K) - standard reference value.
    THERMAL_CONDUCTIVITY_ICE_W_M_K = 2.0
    #: Sea ice density, kg/m^3 - standard reference value.
    ICE_DENSITY_KG_M3 = 917.0
    #: Latent heat of fusion, J/kg.
    LATENT_HEAT_FUSION_J_KG = 3.34e5

    @classmethod
    def ice_growth_rate_m_s(cls, surface_temp_c: float, ice_thickness_m: float, freezing_temp_c: float = -1.8) -> float:
        """
        Stefan's law for sea ice growth by thermal conduction:
        dh/dt = (k_ice / (rho_ice * Lf)) * (Tf - Tsurface) / h.

        NOTE (correction — Physics Guard): this used to be a flat
        linear proxy, (freezing_temp_c - surface_temp_c) * 1.5e-8, with
        no ice_thickness term at all - but the defining physics of
        Stefan's law (what this class's own docstring names it after)
        is that growth rate is INVERSELY proportional to current ice
        thickness (thicker ice conducts heat away more slowly, so it
        grows more slowly) - the previous formula predicted identical
        growth for 10cm-thick and 3m-thick ice at the same temperature,
        contradicting the physics it claimed to implement. A complete,
        correctly thickness-dependent, already-tested implementation of
        this same equation already existed in this codebase
        (science.encyclopedia.cryosphere_extended's
        "sea_ice_thermodynamics_cice" entry, Untersteiner 1965 /
        Hunke & Lipscomb 2008 CICE documentation) - this duplicate was
        missed. Now uses the same real formula and constants.

        Raises
        ------
        ValueError
            If ice_thickness_m <= 0 (the formula divides by it).
        """
        if ice_thickness_m <= 0.0:
            raise ValueError("ice_thickness_m must be positive.")
        if surface_temp_c >= freezing_temp_c:
            return 0.0
        return (
            (cls.THERMAL_CONDUCTIVITY_ICE_W_M_K / (cls.ICE_DENSITY_KG_M3 * cls.LATENT_HEAT_FUSION_J_KG))
            * (freezing_temp_c - surface_temp_c)
            / ice_thickness_m
        )
