"""
ACF GRIB Reader

Reader for GRIB1 / GRIB2 meteorological files.
"""


from pathlib import Path

import xarray as xr

from acf.data.dataset import Dataset
from acf.data.readers.base_reader import BaseReader



class GRIBReader(BaseReader):
    """
    Lecteur de données GRIB.
    """


    name = "GRIB Reader"



    SUPPORTED_EXTENSIONS = (
        ".grib",
        ".grb",
        ".grib2",
        ".grb2",
    )



    ##################################################

    def can_read(self, filename):

        return (
            Path(filename)
            .suffix
            .lower()
            in self.SUPPORTED_EXTENSIONS
        )



    ##################################################

    def read(self, filename):

        filename = Path(filename)


        if not filename.exists():

            raise FileNotFoundError(
                filename
            )



        ds = xr.open_dataset(
            filename,
            engine="cfgrib"
        )



        dataset = Dataset(
            name=filename.stem,
            filepath=filename,
            filetype="GRIB2",
            source="cfgrib",
        )



        # Variables

        for variable in ds.data_vars:

            dataset.add_variable(
                variable
            )



        # Dimensions

        for dim, size in ds.sizes.items():

            dataset.add_dimension(
                dim,
                int(size)
            )



        # Metadata

        for key, value in ds.attrs.items():

            dataset.set_metadata(
                key,
                value
            )



        ds.close()


        dataset.validate()


        return dataset

