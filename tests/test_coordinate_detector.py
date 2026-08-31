from acf.data.engine.coordinate_detector import CoordinateDetector


class DummyDataset:
    def __init__(self):
        self.dimensions = [
            "time",
            "latitude",
            "longitude",
            "level",
        ]


def test_coordinate_detector():

    detector = CoordinateDetector()

    coords = detector.detect(DummyDataset())

    assert coords["latitude"] == "latitude"
    assert coords["longitude"] == "longitude"
    assert coords["time"] == "time"
    assert coords["level"] == "level"
