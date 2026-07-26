from pathlib import Path

from acf.data.dataset import Dataset
from acf.data.dataset_validator import DatasetValidator


def test_validator():

    ds = Dataset(
        name="ERA5",
        filepath=Path("/tmp/test.nc"),
        filetype="NetCDF"
    )

    ds.add_variable("t2m")

    ds.set_dimension("lat", 721)
    ds.set_dimension("lon", 1440)

    ds.set_metadata(
        "coordinates",
        ["lat", "lon"]
    )

    validator = DatasetValidator()

    report = validator.validate(ds)

    assert report["valid"]
from acf.data.engine.dataset_validator import DatasetValidator


class DummyDataset:

    name = "ERA5"

    variables = ["t", "u", "v"]

    dimensions = ["time", "latitude", "longitude"]

    metadata = {}


def test_validator():

    validator = DatasetValidator()

    valid, errors = validator.validate(DummyDataset())

    assert valid

    assert errors == []

    assert validator.is_valid(DummyDataset())
