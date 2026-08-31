from acf.data.engine.dataset_classifier import DatasetClassifier


class Dummy:
    def __init__(self):
        self.metadata = {"model": "WRF"}


def test_classifier():

    classifier = DatasetClassifier()

    assert classifier.classify(Dummy()) == "Regional NWP"
