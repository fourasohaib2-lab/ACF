"""
Atmospheric Complexity Framework (ACF)

Global Carbon Cycle Dynamics Engine Module (Phase 6)
(CarbonCycleEngine modeling Atmosphere, Ocean, Soil, Biosphere, and Lithosphere reservoirs & fluxes)
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class CarbonReservoirs:
    """Reservoirs de carbone planétaires (GtC = GigaTonnes de Carbone)."""

    atmosphere_gtc: float  # ~870 GtC (~425 ppm)
    ocean_gtc: float  # ~38,000 GtC
    soils_permafrost_gtc: float  # ~1,700 GtC
    terrestrial_biosphere_gtc: float  # ~550 GtC
    lithosphere_gtc: float  # ~60,000,000 GtC


@dataclass
class CarbonFluxes:
    """Flux annuels de carbone (GtC/an)."""

    gpp_photosynthesis_gtc_yr: float  # ~120 GtC/yr
    terrestrial_respiration_gtc_yr: float  # ~120 GtC/yr
    ocean_atmosphere_net_sink_gtc_yr: float  # ~2.5 GtC/yr
    fossil_emissions_gtc_yr: float  # ~10.0 GtC/yr
    land_use_emissions_gtc_yr: float  # ~1.2 GtC/yr
    volcanic_emissions_gtc_yr: float  # ~0.1 GtC/yr


class CarbonCycleEngine:
    """
    Moteur de modélisation du cycle du carbone à 5 réservoirs et calcul des puits nets.
    """

    @classmethod
    def get_current_state(cls) -> dict[str, Any]:
        """Retourne l'état actuel des réservoirs et flux du cycle du carbone."""
        reservoirs = CarbonReservoirs(
            atmosphere_gtc=870.0,
            ocean_gtc=38000.0,
            soils_permafrost_gtc=1700.0,
            terrestrial_biosphere_gtc=550.0,
            lithosphere_gtc=60000000.0,
        )
        fluxes = CarbonFluxes(
            gpp_photosynthesis_gtc_yr=120.0,
            terrestrial_respiration_gtc_yr=118.0,
            ocean_atmosphere_net_sink_gtc_yr=2.8,
            fossil_emissions_gtc_yr=10.1,
            land_use_emissions_gtc_yr=1.1,
            volcanic_emissions_gtc_yr=0.1,
        )
        # Bilan net annuel dans l'atmosphère
        net_air_growth_gtc = (fluxes.fossil_emissions_gtc_yr + fluxes.land_use_emissions_gtc_yr) - (
            fluxes.ocean_atmosphere_net_sink_gtc_yr
            + (fluxes.gpp_photosynthesis_gtc_yr - fluxes.terrestrial_respiration_gtc_yr)
        )

        return {
            "reservoirs": reservoirs,
            "fluxes": fluxes,
            "annual_atmospheric_co2_growth_gtc": net_air_growth_gtc,
            "equivalent_ppm_growth_per_year": net_air_growth_gtc / 2.12,  # 1 ppm = 2.12 GtC
        }
