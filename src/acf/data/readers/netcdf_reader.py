"""
ACF NetCDF Reader

Reader for NetCDF meteorological datasets.
"""

from pathlib import Path

import xarray as xr

from acf.catalog.default_mapping import create_default_mapper
from acf.data.dataset import Dataset
from acf.data.readers.base_reader import BaseReader
from acf.data.readers.cf_detector import CFDetector



class NetCDFReader(BaseReader):
    """
    Lecteur de fichiers NetCDF.

    Compatible avec :
    - WRF
    - ICON
    - données climatiques
    - sorties modèles scientifiques
    """


    name = "NetCDF Reader"


    SUPPORTED_EXTENSIONS = (
        ".nc",
        ".nc4",
        ".cdf",
    )



    def __init__(self):

        self.mapper = create_default_mapper()



    ##################################################
    # Détection fichier
    ##################################################

    def can_read(self, filename):

        return (
            Path(filename)
            .suffix
            .lower()
            in self.SUPPORTED_EXTENSIONS
        )



    ##################################################
    # Lecture NetCDF
    ##################################################

    def read(self, filename):

        filename = Path(filename)


        if not filename.exists():

            raise FileNotFoundError(
                filename
            )



        ds = xr.open_dataset(
            filename
        )



        dataset = Dataset(
            name=filename.stem,
            filepath=filename,
            filetype="NETCDF",
            source="xarray",
        )



        ##################################################
        # Variables scientifiques
        ##################################################

        for name, variable in ds.data_vars.items():


            dataset.add_variable(
                name
            )


            dataset.set_metadata(
                f"{name}_acf",
                self.mapper.resolve(name),
            )


            dataset.set_metadata(
                f"{name}_units",
                variable.attrs.get(
                    "units"
                ),
            )


            dataset.set_metadata(
                f"{name}_standard_name",
                variable.attrs.get(
                    "standard_name"
                ),
            )


            dataset.set_metadata(
                f"{name}_long_name",
                variable.attrs.get(
                    "long_name"
                ),
            )


            dataset.set_metadata(
                f"{name}_dtype",
                str(
                    variable.dtype
                ),
            )


            dataset.set_metadata(
                f"{name}_shape",
                tuple(
                    variable.shape
                ),
            )



        ##################################################
        # Dimensions
        ##################################################

        for dim, size in ds.sizes.items():

            dataset.add_dimension(
                dim,
                int(size)
            )



        ##################################################
        # Métadonnées globales
        ##################################################

        for key, value in ds.attrs.items():

            dataset.set_metadata(
                key,
                value
            )



        ##################################################
        # Coordonnées
        ##################################################

        dataset.set_metadata(
            "coordinates",
            list(
                ds.coords
            ),
        )


        dataset.set_metadata(
            "dimensions",
            dict(
                ds.sizes
            ),
        )



        ##################################################
        # Validation
        ##################################################

        dataset.validate()



        ds.close()


        return dataset
