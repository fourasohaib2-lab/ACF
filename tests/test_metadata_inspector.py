from pathlib import Path

from acf.data.dataset import Dataset
from acf.data.metadata_inspector import MetadataInspector


def test_metadata():

    ds = Dataset(name="ERA5", filepath=Path("/tmp/test.nc"), filetype="NetCDF")

    ds.add_variable("t2m")
    ds.add_variable("u10")

    ds.set_dimension("lat", 721)
    ds.set_dimension("lon", 1440)

    ds.set_metadata("institution", "ECMWF")

    inspector = MetadataInspector()

    result = inspector.inspect(ds)

    assert result["summary"]["variable_count"] == 2
    assert result["summary"]["dimension_count"] == 2
    assert result["summary"]["metadata_count"] == 1
