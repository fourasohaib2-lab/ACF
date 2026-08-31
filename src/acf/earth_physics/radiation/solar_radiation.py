"""
Solar Shortwave Radiation Model (S = 1361 W/m^2)
"""


class SolarRadiationModel:
    """Modèle de rayonnement solaire entrant à courte longueur d'onde."""

    SOLAR_CONSTANT = 1361.0  # W/m^2

    @classmethod
    def top_of_atmosphere_insolation(cls, zenith_angle_rad: float) -> float:
        import math

        return max(0.0, cls.SOLAR_CONSTANT * math.cos(zenith_angle_rad))
