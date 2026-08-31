"""
ACF Data Format Detector

Automatic detection of meteorological and Earth observation data formats.
"""


class FormatDetector:
    """
    Détecteur automatique universel des formats scientifiques de données Terre & Météo.
    """

    FORMATS = {
        "GRIB1": [".grib", ".grb", ".grib1"],
        "GRIB2": [".grib2", ".grb2"],
        "NETCDF": [".nc", ".netcdf", ".nc4", ".cdf"],
        "BUFR": [".bufr", ".buf"],
        "HDF5": [".h5", ".hdf5", ".he5", ".hdf"],
        "GEOTIFF": [".tif", ".tiff", ".cog"],
        "CSV": [".csv", ".tsv"],
        "JSON": [".json", ".geojson"],
        "XML": [".xml", ".kml"],
        "FA": [".fa", ".fa.gz"],
        "LFA": [".lfa"],
        "LFI": [".lfi"],
        "ZARR": [".zarr"],
        "PARQUET": [".parquet", ".pq"],
        "ARROW": [".arrow", ".ipc"],
    }

    @classmethod
    def detect(cls, filepath) -> str:
        """Détecte le format canonique d'un fichier à partir de son extension ou de sa structure."""
        path_str = str(filepath).lower()

        for name, extensions in cls.FORMATS.items():
            for ext in extensions:
                if path_str.endswith(ext):
                    return name

        return "UNKNOWN"

    @classmethod
    def supported_formats(cls) -> list[str]:
        """Retourne la liste des formats supportés."""
        return list(cls.FORMATS.keys())

    @classmethod
    def is_supported(cls, filepath) -> bool:
        """Vérifie si le fichier est supporté par ACF."""
        return cls.detect(filepath) != "UNKNOWN"
