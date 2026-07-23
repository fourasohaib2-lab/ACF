from acf.science.engine import ScienceEngine


def test_engine():

    engine = ScienceEngine()

    modules = engine.available()

    assert "thermodynamics" in modules
    assert "dynamics" in modules
    assert "severe_weather" in modules
