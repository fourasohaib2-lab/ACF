from pathlib import Path

from acf.data.dataset import Dataset
from acf.models.manager import ModelManager


def test_manager():

    manager = ModelManager()

    assert "ERA5" in manager.models()

    ds = Dataset(
        name="ERA5",
        filepath=Path("/tmp/test.nc"),
        filetype="NetCDF",
    )

    ds.set_metadata(
        "institution",
        "ECMWF",
    )

    model = manager.detect(ds)

    assert model is not None

    assert model.name == "ERA5"
