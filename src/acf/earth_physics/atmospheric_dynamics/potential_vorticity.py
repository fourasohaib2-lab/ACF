"""
Ertel's Potential Vorticity (PV = (1/rho) * (zeta + f) * dTheta/dz)
"""


class ErtelsPotentialVorticity:
    """Calculateur de la vorticité potentielle d'Ertel (PVU)."""

    @classmethod
    def compute_pv(cls, abs_vorticity: float, dtheta_dz: float, rho: float = 1.225) -> float:
        pv_si = (1.0 / rho) * abs_vorticity * dtheta_dz
        return pv_si * 1.0e6  # Convert to PVU (10^-6 K m^2 kg^-1 s^-1)
