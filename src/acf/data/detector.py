"""
ACF Data Format Detector

Automatic detection of meteorological data formats.
"""


from pathlib import Path



class FormatDetector:
    """
    Détecteur automatique des formats scientifiques.
    """



    FORMATS = {

        "GRIB1": [
            ".grib",
            ".grb",
        ],


        "GRIB2": [
            ".grib2",
            ".grb2",
        ],


        "NETCDF": [
            ".nc",
            ".netcdf",
        ],


        "BUFR": [
            ".bufr",
        ],


        "HDF5": [
            ".h5",
            ".hdf5",
        ],


        "GEOTIFF": [
            ".tif",
            ".tiff",
        ],


        "CSV": [
            ".csv",
        ],

    }



    ##################################################

    @classmethod
    def detect(cls, filepath):

        path = Path(filepath)

        extension = (
            path.suffix
            .lower()
        )


        for name, extensions in cls.FORMATS.items():

            if extension in extensions:

                return name



        return "UNKNOWN"



    ##################################################

    @classmethod
    def supported_formats(cls):

        return list(
            cls.FORMATS.keys()
        )



    ##################################################

    @classmethod
    def is_supported(cls, filepath):

        return (
            cls.detect(filepath)
            != "UNKNOWN"
        )
