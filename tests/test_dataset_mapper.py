from pathlib import Path

from acf.data.dataset import Dataset
from acf.data.integration.dataset_mapper import DatasetMapper


def test_mapper():

    ds = Dataset(
        name="ERA5",
        filepath=Path("/tmp/test.nc"),
        filetype="NetCDF",
    )

    mapper = DatasetMapper()

    mapped = mapper.map(ds)

    assert mapped.name == "ERA5"


def test_copy():

    ds = Dataset(
        name="GFS",
        filepath=Path("/tmp/gfs.nc"),
        filetype="NetCDF",
    )

    mapper = DatasetMapper()

    copied = mapper.copy(ds)

    assert copied.name == ds.name

    assert copied.filetype == ds.filetype

    assert copied is not ds
