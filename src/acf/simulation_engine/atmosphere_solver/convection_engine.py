"""Convective parameterization engine for deep and shallow convection."""

from enum import Enum
from typing import Dict, Tuple
import numpy as np


class ConvectionScheme(Enum):
    """Supported convective parameterization schemes."""

    KAIN_FRITSCH = "Kain-Fritsch"
    TIEDTKE = "Tiedtke"
    MASS_FLUX = "Mass-Flux"


class ConvectionEngine:
    """Convective parameterization solver.

    Calculates thermodynamic parcel stability indices:
    - CAPE (Convective Available Potential Energy, J/kg)
    - CIN (Convective Inhibition, J/kg)
    - LFC (Level of Free Convection, m / Pa)
    - EL (Equilibrium Level, m / Pa)
    - Entrainment rate (1/m)
    """

    def __init__(self, scheme: ConvectionScheme = ConvectionScheme.KAIN_FRITSCH) -> None:
        self.scheme = scheme
        self.g = 9.80665  # Gravity acceleration (m/s^2)

    def calculate_cape_cin(
        self, temp_profile: np.ndarray, pressure_profile: np.ndarray, q_profile: np.ndarray
    ) -> Tuple[float, float, float, float]:
        """Compute CAPE, CIN, LFC, EL for a 1D vertical atmospheric column.

        Args:
            temp_profile (np.ndarray): 1D temperature profile (K), surface to top.
            pressure_profile (np.ndarray): 1D pressure profile (Pa).
            q_profile (np.ndarray): 1D specific humidity (kg/kg).

        Returns:
            Tuple[float, float, float, float]: (CAPE, CIN, LFC_Pa, EL_Pa)
        """
        # Parcel starting at surface (level 0)
        t_parcel = temp_profile[0] + 1.5  # Parcel temperature with thermal boost
        p_parcel = pressure_profile[0]

        cape = 0.0
        cin = 0.0
        lfc_p = pressure_profile[0]
        el_p = pressure_profile[-1]

        found_lfc = False

        for k in range(len(temp_profile)):
            p_curr = pressure_profile[k]
            t_env = temp_profile[k]

            # Dry adiabatic ascent proxy
            t_parcel_curr = t_parcel * (p_curr / p_parcel) ** (0.286)

            buoyancy = self.g * (t_parcel_curr - t_env) / t_env

            if buoyancy > 0:
                if not found_lfc:
                    lfc_p = p_curr
                    found_lfc = True
                cape += buoyancy * 100.0  # Approx vertical integration step
                el_p = p_curr
            else:
                if not found_lfc:
                    cin += abs(buoyancy) * 100.0

        return float(np.clip(cape, 0.0, 6000.0)), float(np.clip(cin, 0.0, 1000.0)), float(lfc_p), float(el_p)

    def compute_convective_mass_flux(
        self, cape_field: np.ndarray, cin_field: np.ndarray, entrainment_rate: float = 1e-4
    ) -> Dict[str, np.ndarray]:
        """Calculate mass flux M_u = rho * w_up * area_fraction based on scheme.

        Args:
            cape_field (np.ndarray): 2D CAPE array (J/kg).
            cin_field (np.ndarray): 2D CIN array (J/kg).
            entrainment_rate (float): Fractional entrainment rate per meter.

        Returns:
            Dict[str, np.ndarray]: Convective mass flux and convective precipitation rate.
        """
        # Trigger condition: CAPE > CIN and CAPE > 250 J/kg
        active_convection = (cape_field > cin_field) & (cape_field > 250.0)

        # Updraft velocity w ~ sqrt(2 * CAPE)
        w_up = np.where(active_convection, np.sqrt(2.0 * cape_field), 0.0)

        # Convective mass flux proxy (kg/m^2/s)
        mass_flux = 0.05 * w_up * (1.0 - np.exp(-entrainment_rate * 5000.0))

        # Convective rain rate (mm/h)
        conv_precip = np.where(active_convection, 0.1 * mass_flux * 3600.0, 0.0)

        return {
            "mass_flux": mass_flux,
            "convective_precip": conv_precip,
            "active_mask": active_convection,
        }
