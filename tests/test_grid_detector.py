from acf.data.engine.grid_detector import GridDetector


class DummyDataset:

    dimensions = ["time", "latitude", "longitude"]

    metadata = {}


def test_grid_detector():

    detector = GridDetector()

    assert detector.detect(DummyDataset()) == "Regular Lat/Lon"

    assert detector.is_regular(DummyDataset())
