"""
Atmospheric Complexity Framework (ACF)

Solar Radiation Management (SRM) Geoengineering Engine Module (Phase 2)
(SolarRadiationManagementEngine modeling SAI, MCB, CCT, Space Reflectors, and Surface Albedo)
"""

from dataclasses import dataclass


CLIMATE_SENSITIVITY_LAMBDA = 0.8  # K per (W/m^2)


@dataclass
class SRMResult:
    """Résultat physique d'une intervention de gestion du rayonnement solaire (SRM)."""
    technique_name: str
    radiative_forcing_w_m2: float
    global_temperature_cooling_k: float
    regional_monsoon_disruption_pct: float
    termination_shock_risk_level: str
    side_effects: list[str]


class SolarRadiationManagementEngine:
    """
    Moteur de simulation physique des techniques de gestion du rayonnement solaire (SRM).
    """

    @classmethod
    def simulate_stratospheric_aerosol_injection(cls, so2_injection_megatons_per_year: float = 5.0) -> SRMResult:
        """
        Simule l'injection d'aérosols de dioxyde de soufre (SO2) dans la stratosphère (SAI).
        
        Equations:
            \\Delta F = -0.45 \\cdot \\text{SO2}_{\\text{Mt/yr}}
            \\Delta T = \\lambda \\cdot \\Delta F
        """
        forcing = -0.45 * so2_injection_megatons_per_year
        cooling = abs(CLIMATE_SENSITIVITY_LAMBDA * forcing)
        disruption = 1.2 * so2_injection_megatons_per_year  # % de réduction des précipitations en mousson Asie/Afrique

        return SRMResult(
            technique_name="Stratospheric Aerosol Injection (SAI)",
            radiative_forcing_w_m2=forcing,
            global_temperature_cooling_k=cooling,
            regional_monsoon_disruption_pct=disruption,
            termination_shock_risk_level="HIGH (Rapid warming if injection halts abruptly)",
            side_effects=[
                "Stratospheric Ozone Layer Depletion",
                "Modification of Sky Color (Diffuse Solar Radiation)",
                "Disruption of Indian and West African Monsoons",
            ],
        )

    @classmethod
    def simulate_marine_cloud_brightening(cls, sea_salt_injection_rate_t_s: float = 100.0) -> SRMResult:
        """Simule l'éclaircissement des nuages marins (MCB) par pulvérisation d'aérosols de sel marin."""
        forcing = -0.15 * (sea_salt_injection_rate_t_s / 10.0)
        cooling = abs(CLIMATE_SENSITIVITY_LAMBDA * forcing)

        return SRMResult(
            technique_name="Marine Cloud Brightening (MCB)",
            radiative_forcing_w_m2=forcing,
            global_temperature_cooling_k=cooling,
            regional_monsoon_disruption_pct=0.5,
            termination_shock_risk_level="MEDIUM",
            side_effects=["Regional Precipitation Alterations over Coastal Oceans"],
        )
