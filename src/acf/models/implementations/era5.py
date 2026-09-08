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
        """
        Detect if the dataset belongs to ERA5 (ECMWF reanalysis).

        NOTE (correction): this used to access dataset.metadata
        unconditionally, crashing with AttributeError whenever
        `dataset` wasn't a metadata-bearing object - which includes
        the single most obvious call, ModelManager().detect(some_path
        or filename string), since ERA5Model is ModelManager's only
        built-in registered model. Every sibling detect() elsewhere in
        this package (ARPEGE/AROME/ALADIN) returns False for input it
        doesn't recognize rather than raising; this now matches that
        contract instead of crashing the whole detection pipeline.
        """
        metadata = getattr(dataset, "metadata", None)
        if not isinstance(metadata, dict):
            return False

        institution = metadata.get("institution", "")
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
