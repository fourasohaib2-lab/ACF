"""
ERA5 Weather Model
"""

from acf.models.base_model import BaseWeatherModel


class ERA5Model(BaseWeatherModel):

    name = "ERA5"

    supported_extensions = (
        ".nc",
        ".grib",
        ".grib2",
    )

    def detect(self, dataset):

        institution = dataset.metadata.get("institution", "")

        return "ECMWF" in institution

    def variables(self):

        return [
            "t2m",
            "d2m",
            "u10",
            "v10",
            "msl",
            "sp",
            "tp",
            "z",
            "r",
            "q",
        ]

    def levels(self):

        return "pressure"

    def projection(self):

        return "latlon"
