"""
Coriolis Parameter Module (f = 2 * Omega * sin(latitude))
"""

import math


class CoriolisParam:
    """Calculateur du paramètre de Coriolis f et du paramètre beta."""

    OMEGA_EARTH = 7.2921159e-5  # rad/s

    @classmethod
    def f_parameter(cls, lat_deg: float) -> float:
        lat_rad = math.radians(lat_deg)
        return 2.0 * cls.OMEGA_EARTH * math.sin(lat_rad)
