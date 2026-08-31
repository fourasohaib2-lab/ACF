from acf.data.engine.dataset_metadata import DatasetMetadata


class DummyDataset:
    def __init__(self):
        self.name = "ERA5"
        self.variables = ["t", "u"]
        self.dimensions = ["time", "lat", "lon"]
        self.metadata = {
            "model": "ERA5",
            "institution": "ECMWF",
            "source": "Copernicus",
        }


def test_metadata():

    extractor = DatasetMetadata()

    info = extractor.extract(DummyDataset())

    assert info["name"] == "ERA5"

    assert info["model"] == "ERA5"

    assert info["institution"] == "ECMWF"

    assert info["variables"] == 2

    assert extractor.has_metadata(DummyDataset())
