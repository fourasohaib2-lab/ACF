"""
Severe Weather Engine
=====================
"""

from acf.science.cape import CAPE
from acf.science.cin import CIN
from acf.science.bulk_wind_shear import BulkWindShear
from acf.science.storm_relative_helicity import StormRelativeHelicity


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
