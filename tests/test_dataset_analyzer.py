import numpy as np

from acf.ai.analyzers.dataset_analyzer import DatasetAnalyzer


def test_summary():

    analyzer = DatasetAnalyzer()

    dataset = {"temperature": np.array([[20, 21], [22, 23]]), "pressure": np.array([[1010, 1012], [1011, 1013]])}

    result = analyzer.summary(dataset)

    assert result["count"] == 2

    assert "temperature" in result["variables"]


def test_statistics():

    analyzer = DatasetAnalyzer()

    dataset = {"temperature": np.array([10, 20, 30])}

    report = analyzer.analyze(dataset)

    assert report["temperature"]["min"] == 10.0
    assert report["temperature"]["max"] == 30.0
    assert report["temperature"]["mean"] == 20.0
