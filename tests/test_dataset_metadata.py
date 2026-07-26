from acf.data.engine.dataset_metadata import DatasetMetadata


class DummyDataset:

    name = "ERA5"

    variables = ["t", "u"]

    dimensions = ["time", "lat", "lon"]

    metadata = {

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
