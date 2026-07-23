from acf.science.engine import ScienceEngine


def test_engine():

    engine = ScienceEngine()

    engines = engine.available()

    assert "thermodynamics" in engines
    assert "dynamics" in engines
    assert "severe_weather" in engines

