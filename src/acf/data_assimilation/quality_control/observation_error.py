"""
Observation Error Covariance & Error Modeling Module (Obs = Value + Error)
"""


class ObservationErrorModel:
    """Modélisation de l'erreur d'observation (Instrumental + Représentativité + Biais)."""

    @classmethod
    def get_observation_error_std(cls, sensor_type: str = "SYNOP_Thermometer") -> float:
        if sensor_type == "SYNOP_Thermometer":
            return 0.2  # K
        elif sensor_type == "Satellite_IR":
            return 1.2  # K
        return 1.0
