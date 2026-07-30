"""
Severe Weather Engine
=====================
"""



class SevereWeather:
    """
    Severe weather diagnostic engine.
    """

    @staticmethod
    def summary(
        cape: float,
        cin: float,
        shear: float,
        srh: float,
    ) -> dict:

        return {
            "cape": cape,
            "cin": cin,
            "bulk_shear": shear,
            "srh": srh,
        }
