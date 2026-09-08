from acf.data.engine.grid_detector import GridDetector


class DummyDataset:
    def __init__(self):
        self.dimensions = ["time", "latitude", "longitude"]
        self.metadata = {}


def test_grid_detector():

    detector = GridDetector()

    assert detector.detect(DummyDataset()) == "Regular Lat/Lon"

    assert detector.is_regular(DummyDataset())
