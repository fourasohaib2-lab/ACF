"""
Geostrophic Balance Module (u_g = -(1/(f*rho))*dp/dy, v_g = (1/(f*rho))*dp/dx)
"""


class GeostrophicBalance:
    """Calculateur du vent géostrophique."""

    @classmethod
    def compute_geostrophic_wind(cls, dp_dx: float, dp_dy: float, f: float, rho: float = 1.225) -> tuple:
        if abs(f) < 1.0e-10:
            return 0.0, 0.0
        u_g = -(1.0 / (f * rho)) * dp_dy
        v_g = (1.0 / (f * rho)) * dp_dx
        return u_g, v_g
