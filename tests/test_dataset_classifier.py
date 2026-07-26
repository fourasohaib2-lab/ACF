from acf.data.engine.dataset_classifier import DatasetClassifier


class Dummy:

    metadata = {
        "model": "WRF"
    }


def test_classifier():

    classifier = DatasetClassifier()

    assert classifier.classify(Dummy()) == "Regional NWP"
