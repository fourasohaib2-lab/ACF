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

    dataset.set_metadata("institution", "ECMWF")

    model = detector.detect(dataset)

    assert model is not None
    assert model.name == "ERA5"


def test_detector_does_not_crash_on_plain_string_input():
    """
    CORRECTED: ERA5Model.detect() used to access dataset.metadata
    unconditionally, crashing with AttributeError for any input
    without a .metadata attribute - including the single most obvious
    call, a plain path/filename string, which is exactly what
    ModelManager's only built-in registered model would receive from
    a caller following the same convention as every other adapter in
    this package (ARPEGE/AROME/ALADIN all accept a plain string/Path).
    See era5.py.
    """
    registry = ModelRegistry()
    registry.register(ERA5Model())
    detector = ModelDetector(registry)

    assert detector.detect("/data/some_file.grib2") is None
