"""
Atmospheric Complexity Framework (ACF)

Adapter Factory
"""

from pathlib import Path

from acf.data.integration.bufr_adapter import BUFRAdapter
from acf.data.integration.csv_adapter import CSVAdapter
from acf.data.integration.geotiff_adapter import GeoTIFFAdapter
from acf.data.integration.grib_adapter import GRIBAdapter
from acf.data.integration.hdf5_adapter import HDF5Adapter
from acf.data.integration.json_adapter import JSONAdapter
from acf.data.integration.netcdf_adapter import NetCDFAdapter
from acf.data.integration.xml_adapter import XMLAdapter


class AdapterFactory:
    """
    Automatically selects the correct adapter.
    """

    def __init__(self):

        self.adapters = [
            NetCDFAdapter(),
            GRIBAdapter(),
            BUFRAdapter(),
            JSONAdapter(),
            XMLAdapter(),
            HDF5Adapter(),
            GeoTIFFAdapter(),
            CSVAdapter(),
        ]

    ##########################################################

    def get_adapter(self, filepath):

        path = Path(filepath)

        for adapter in self.adapters:
            if adapter.supports(path):
                return adapter

        raise ValueError(f"No adapter available for {path}")

    ##########################################################

    def load(self, filepath):

        adapter = self.get_adapter(filepath)

        return adapter.load(Path(filepath))
