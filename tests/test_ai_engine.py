from acf.ai.engine import AIEngine


def test_engine_creation():

    engine = AIEngine()

    assert engine.version == "0.1.0"


def test_register_model():

    engine = AIEngine()

    engine.register_model("forecast", object())

    assert "forecast" in engine.available_models()


def test_history():

    engine = AIEngine()

    engine.analyze({})

    assert engine.history_count() == 1

    engine.clear_history()

    assert engine.history_count() == 0
