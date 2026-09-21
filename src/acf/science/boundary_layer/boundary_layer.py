"""
Atmospheric Boundary Layer
===========================

Computable implementations backing science/laws/boundary_layer.py's
BOUNDARY_LAYER_LAWS entries (some of which — e.g. monin_obukhov_length
— previously had no compute_func at all, meaning calling
ScientificRegistry.get("monin_obukhov_length").calculate() raised
NotImplementedError despite the law being documented; fixed here).

Reference:
    Stull, R. B. (1988). "An Introduction to Boundary Layer
    Meteorology". Kluwer Academic Publishers.
    Garratt, J. R. (1992). "The Atmospheric Boundary Layer".
    Cambridge University Press.
"""

import math

from acf.science.constants import CP, EPSILON, G, LV

VON_KARMAN = 0.40


class MoninObukhovLength:
    """Monin-Obukhov length L (m)."""

    @staticmethod
    def calculate(friction_velocity: float, virtual_temperature_k: float, kinematic_heat_flux: float) -> float:
        """
        L = - (u*^3 * Tv) / (kappa * g * w'theta'_0)

        Parameters
        ----------
        friction_velocity : float
            u* (m/s), > 0.
        virtual_temperature_k : float
            Reference virtual temperature (K), > 0.
        kinematic_heat_flux : float
            Surface kinematic heat flux w'theta'_0 (K*m/s). Positive
            for unstable (daytime, surface heating) conditions.

        Returns
        -------
        float
            L (m). Negative under unstable conditions, positive under
            stable conditions, +/-infinity as the flux -> 0 (neutral).

        Raises
        ------
        ValueError
            If friction_velocity or virtual_temperature_k are non-positive.

        Reference
        ---------
        Stull (1988), Ch. 5.
        """
        if friction_velocity <= 0:
            raise ValueError("friction_velocity must be positive.")
        if virtual_temperature_k <= 0:
            raise ValueError("virtual_temperature_k must be positive.")
        if kinematic_heat_flux == 0:
            return math.inf

        return -(friction_velocity**3 * virtual_temperature_k) / (VON_KARMAN * G * kinematic_heat_flux)

    @staticmethod
    def stability_regime(monin_obukhov_length: float, height_m: float) -> str:
        """
        Classify surface-layer stability from z/L (Stull 1988 convention).
        """
        if math.isinf(monin_obukhov_length):
            return "Neutral"
        zeta = height_m / monin_obukhov_length
        if zeta < -0.1:
            return "Unstable"
        if zeta > 0.1:
            return "Stable"
        return "Neutral"


class FrictionVelocity:
    """Friction velocity u* (m/s) from the neutral logarithmic wind profile."""

    @staticmethod
    def calculate(wind_speed: float, height_m: float, roughness_length_m: float) -> float:
        """
        u* = kappa * U(z) / ln(z/z0)   (neutral surface layer)

        Parameters
        ----------
        wind_speed : float
            Wind speed U(z) at height z (m/s), >= 0.
        height_m : float
            Measurement height z (m), > roughness_length_m.
        roughness_length_m : float
            Surface roughness length z0 (m), > 0.

        Returns
        -------
        float
            u* (m/s).

        Reference
        ---------
        Stull (1988), Ch. 9. Same formula as the registered law
        'logarithmic_wind_profile', inverted for u*.
        """
        if wind_speed < 0:
            raise ValueError("wind_speed must be non-negative.")
        if roughness_length_m <= 0:
            raise ValueError("roughness_length_m must be positive.")
        if height_m <= roughness_length_m:
            raise ValueError("height_m must exceed roughness_length_m.")

        return VON_KARMAN * wind_speed / math.log(height_m / roughness_length_m)


class BowenRatio:
    """Bowen ratio (H/LE) via the surface energy balance method."""

    @staticmethod
    def psychrometric_constant(pressure_hpa: float) -> float:
        """
        gamma = Cp * p / (epsilon * Lv)   (hPa/K, i.e. same units as
        vapor pressure per degree — consistent with delta_e in hPa).

        Reference
        ---------
        Bowen, I. S. (1926). Phys. Rev., 27(6), 779-787.
        """
        if pressure_hpa <= 0:
            raise ValueError("pressure_hpa must be positive.")
        return CP * pressure_hpa / (EPSILON * LV)

    @staticmethod
    def calculate(delta_temperature_k: float, delta_vapor_pressure_hpa: float, pressure_hpa: float) -> float:
        """
        beta = H/LE = gamma * delta_T / delta_e

        Parameters
        ----------
        delta_temperature_k : float
            Temperature difference between two levels (K or degC, same
            magnitude either way since it's a difference).
        delta_vapor_pressure_hpa : float
            Vapor pressure difference between the same two levels (hPa).
        pressure_hpa : float
            Atmospheric pressure (hPa), for the psychrometric constant.

        Returns
        -------
        float
            Bowen ratio (dimensionless).

        Raises
        ------
        ValueError
            If delta_vapor_pressure_hpa is zero (undefined ratio) or
            pressure_hpa is non-positive.

        Reference
        ---------
        Bowen, I. S. (1926). Phys. Rev., 27(6), 779-787. Standard
        Bowen Ratio Energy Balance (BREB) method formulation.
        """
        if delta_vapor_pressure_hpa == 0:
            raise ValueError("delta_vapor_pressure_hpa must not be zero.")
        gamma = BowenRatio.psychrometric_constant(pressure_hpa)
        return gamma * delta_temperature_k / delta_vapor_pressure_hpa

    @staticmethod
    def partition_fluxes(net_radiation_w_m2: float, soil_heat_flux_w_m2: float, bowen_ratio: float) -> dict:
        """
        Partition available energy (Rn - G) into sensible (H) and
        latent (LE) heat flux using the Bowen ratio, via the surface
        energy balance closure Rn - G = H + LE.

            H  = beta / (1+beta) * (Rn - G)
            LE = 1    / (1+beta) * (Rn - G)

        Parameters
        ----------
        net_radiation_w_m2 : float
            Net radiation Rn (W/m^2).
        soil_heat_flux_w_m2 : float
            Ground/soil heat flux G (W/m^2).
        bowen_ratio : float
            Bowen ratio (H/LE), e.g. from calculate().

        Returns
        -------
        dict
            {"sensible_heat_flux_w_m2": H, "latent_heat_flux_w_m2": LE}

        Raises
        ------
        ValueError
            If bowen_ratio == -1 (division by zero — available energy
            cannot be partitioned when H = -LE exactly).
        """
        if bowen_ratio == -1:
            raise ValueError("bowen_ratio of exactly -1 makes flux partitioning undefined (H = -LE).")

        available_energy = net_radiation_w_m2 - soil_heat_flux_w_m2
        h = bowen_ratio / (1.0 + bowen_ratio) * available_energy
        le = available_energy / (1.0 + bowen_ratio)

        return {"sensible_heat_flux_w_m2": h, "latent_heat_flux_w_m2": le}


class PBLHeight:
    """Convective boundary layer (mixed-layer) height via the parcel method."""

    @staticmethod
    def parcel_method(
        height_profile_m: list[float],
        potential_temperature_profile_k: list[float],
        surface_potential_temperature_k: float,
        excess_k: float = 0.0,
    ) -> float:
        """
        Convective PBL height Zi: the height at which a rising dry
        thermal (starting at the surface potential temperature, plus
        an optional small excess) first becomes neutrally buoyant,
        i.e. where the environmental theta(z) profile first equals or
        exceeds theta_surface + excess. Linear interpolation between
        bracketing levels.

        Parameters
        ----------
        height_profile_m : list of float
            Heights (m), strictly increasing, >= 2 levels.
        potential_temperature_profile_k : list of float
            Environmental potential temperature at each height (K),
            same length as height_profile_m.
        surface_potential_temperature_k : float
            Surface (or near-surface mixed layer) potential
            temperature (K).
        excess_k : float
            Small superadiabatic excess added to the surface value
            (K), commonly 0.5-1 K in operational implementations of
            this method. Defaults to 0 (no excess).

        Returns
        -------
        float
            Zi (m). Returns the top of the profile if theta(z) never
            reaches the threshold within the supplied levels (i.e. the
            profile doesn't extend high enough to bracket Zi) — this
            is a real limitation of finite input data, not silently
            hidden.

        Raises
        ------
        ValueError
            If profiles have inconsistent lengths or fewer than 2 levels.

        Reference
        ---------
        Holzworth, G. C. (1964). "Estimates of Mean Maximum Mixing
        Depths in the Contiguous United States". Mon. Wea. Rev., 92(5),
        235-242. (The classic "parcel method" for convective PBL depth.)
        """
        n = len(height_profile_m)
        if len(potential_temperature_profile_k) != n:
            raise ValueError("height and potential temperature profiles must have the same length.")
        if n < 2:
            raise ValueError("at least two levels are required.")

        threshold = surface_potential_temperature_k + excess_k

        for i in range(n - 1):
            theta_below, theta_above = potential_temperature_profile_k[i], potential_temperature_profile_k[i + 1]
            if theta_below >= threshold:
                return height_profile_m[i]
            if theta_above >= threshold:
                # Linear interpolation between the two bracketing levels.
                z_below, z_above = height_profile_m[i], height_profile_m[i + 1]
                frac = (threshold - theta_below) / (theta_above - theta_below)
                return z_below + frac * (z_above - z_below)

        # Profile never reaches the threshold: Zi is at or above the top level.
        return height_profile_m[-1]
