"""
Wind Turbulence
================

Clear-air turbulence indices (Ellrod & Knapp 1992), jet stream
detection, and mechanical TKE production. SRH and Richardson number
already live in science/stability.py / science/bulk_richardson_number.py
and science/laws/boundary_layer.py — not duplicated here.

Reference:
    Ellrod, G. P., & Knapp, D. I. (1992). "An Objective Clear-Air
    Turbulence Forecasting Technique: Verification and Operational
    Use". Weather and Forecasting, 7(1), 150-165.
"""

import math

from acf.science.constants import G

JET_STREAM_THRESHOLD_M_S = 30.0


class CATIndex:
    """Ellrod & Knapp (1992) clear-air turbulence indices (TI1/EI, TI2)."""

    @staticmethod
    def vertical_wind_shear(du_dz: float, dv_dz: float) -> float:
        """VWS = sqrt((du/dz)^2 + (dv/dz)^2), units s^-1."""
        return math.sqrt(du_dz**2 + dv_dz**2)

    @staticmethod
    def deformation(du_dx: float, dv_dy: float, dv_dx: float, du_dy: float) -> float:
        """
        DEF = sqrt(DSH^2 + DST^2)
        DST (stretching) = du/dx - dv/dy ; DSH (shearing) = dv/dx + du/dy
        Units s^-1.
        """
        stretching = du_dx - dv_dy
        shearing = dv_dx + du_dy
        return math.sqrt(shearing**2 + stretching**2)

    @staticmethod
    def convergence(du_dx: float, dv_dy: float) -> float:
        """CVG = -(du/dx + dv/dy), units s^-1 (= negative divergence)."""
        return -(du_dx + dv_dy)

    @staticmethod
    def ti1(vertical_wind_shear: float, deformation: float) -> float:
        """
        TI1 = VWS * DEF  (shear instability / frontogenesis component only).
        Units s^-2.
        """
        return vertical_wind_shear * deformation

    @staticmethod
    def ti2(vertical_wind_shear: float, deformation: float, convergence: float) -> float:
        """
        TI2 (= Ellrod Index EI) = VWS * (DEF + CVG).
        Units s^-2. Conventionally reported as x1e7 s^-2 in operational
        use — this method returns the raw s^-2 value; multiply by 1e7
        to compare directly against the textbook threshold table
        (4=light-moderate, 8=moderate, 12=moderate-severe).

        Reference
        ---------
        Ellrod & Knapp (1992), Wea. Forecasting, 7(1), 150-165.
        """
        return vertical_wind_shear * (deformation + convergence)

    @staticmethod
    def category(ti2_value_s2: float) -> str:
        """
        Classify a TI2/EI value (raw s^-2) into a turbulence severity
        category using the standard x1e7-scaled thresholds
        (4/8/12 -> 4e-7/8e-7/12e-7 s^-2).
        """
        scaled = ti2_value_s2 * 1e7
        if scaled < 4:
            return "Smooth to Light"
        if scaled < 8:
            return "Light-Moderate"
        if scaled < 12:
            return "Moderate"
        return "Moderate-Severe"


class JetStream:
    """Jet stream detection from wind speed."""

    @staticmethod
    def is_jet_stream(wind_speed_m_s: float) -> bool:
        """
        True if wind_speed_m_s meets the standard jet-stream threshold
        (>= 30 m/s, ~58 kt), the widely used textbook definition for
        an upper-level jet streak.
        """
        return wind_speed_m_s >= JET_STREAM_THRESHOLD_M_S


class TKEProduction:
    """Mechanical (shear) production of turbulent kinetic energy, K-theory closure."""

    @staticmethod
    def mechanical_production(eddy_viscosity_km: float, du_dz: float, dv_dz: float) -> float:
        """
        P_mech = Km * ((du/dz)^2 + (dv/dz)^2)

        Parameters
        ----------
        eddy_viscosity_km : float
            Eddy viscosity Km (m^2/s), >= 0 (a K-theory closure
            parameter — ACF does not yet compute Km itself from a
            mixing-length or TKE-closure scheme; it is a required
            input here).
        du_dz, dv_dz : float
            Vertical wind shear components (s^-1).

        Returns
        -------
        float
            Mechanical TKE production rate (m^2/s^3), always >= 0
            (mechanical/shear production is never a sink).

        Reference
        ---------
        Stull (1988), Ch. 5 — standard K-theory closure form.
        """
        if eddy_viscosity_km < 0:
            raise ValueError("eddy_viscosity_km must be non-negative.")
        return eddy_viscosity_km * (du_dz**2 + dv_dz**2)

    @staticmethod
    def buoyancy_production(eddy_diffusivity_kh: float, potential_temperature_k: float, dtheta_dz: float) -> float:
        """
        P_buoy = (g/theta) * Kh * (-dtheta/dz)

        Positive (source) when the layer is unstable/superadiabatic
        (dtheta/dz < 0); negative (sink) when stable (dtheta/dz > 0).

        Parameters
        ----------
        eddy_diffusivity_kh : float
            Eddy diffusivity for heat Kh (m^2/s), >= 0.
        potential_temperature_k : float
            Reference potential temperature (K), > 0.
        dtheta_dz : float
            Vertical potential temperature gradient (K/m).

        Returns
        -------
        float
            Buoyancy TKE production rate (m^2/s^3).
        """
        if eddy_diffusivity_kh < 0:
            raise ValueError("eddy_diffusivity_kh must be non-negative.")
        if potential_temperature_k <= 0:
            raise ValueError("potential_temperature_k must be positive.")
        return (G / potential_temperature_k) * eddy_diffusivity_kh * (-dtheta_dz)
