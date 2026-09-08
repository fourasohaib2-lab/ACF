from acf.data.engine.projection_detector import ProjectionDetector


def test_latlon_projection():

    detector = ProjectionDetector()

    attrs = {"grid_mapping_name": "latitude_longitude"}

    assert detector.detect(attrs) == "latlon"


def test_lambert_projection():

    detector = ProjectionDetector()

    attrs = {"grid_mapping_name": "lambert_conformal_conic"}

    assert detector.detect(attrs) == "lambert"


def test_mercator_projection():

    detector = ProjectionDetector()

    attrs = {"grid_mapping_name": "mercator"}

    assert detector.detect(attrs) == "mercator"


def test_unknown_projection():

    detector = ProjectionDetector()

    attrs = {}

    assert detector.detect(attrs) == "unknown"


class DummyDataset:
    def __init__(self):
        self.dimensions = [
            "latitude",
            "longitude",
        ]
        self.metadata = {}


def test_projection_detector():

    detector = ProjectionDetector()

    assert detector.detect(DummyDataset()) == "EPSG:4326"

    assert detector.is_geographic(DummyDataset())
