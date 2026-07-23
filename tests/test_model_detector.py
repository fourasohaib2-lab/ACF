from pathlib import Path

from acf.data.dataset import Dataset
from acf.models.detector import ModelDetector
from acf.models.implementations.era5 import ERA5Model
from acf.models.registry import ModelRegistry


def test_detector():

    registry = ModelRegistry()

    registry.register(ERA5Model())

    detector = ModelDetector(registry)

    dataset = Dataset(
        name="ERA5",
        filepath=Path("/tmp/test.nc"),
        filetype="NetCDF",
    )

    dataset.set_metadata(
        "institution",
        "ECMWF"
    )

    model = detector.detect(dataset)

    assert model is not None
    assert model.name == "ERA5"
