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


def test_analyze_does_not_fake_success():
    """
    CORRECTED: analyze() used to unconditionally report
    "status": "success" regardless of the dataset - no model is ever
    actually invoked. See engine.py's own NOTE (correction).
    """
    engine = AIEngine()

    result = engine.analyze({"t2m": [1, 2, 3]})

    assert result["status"] != "success"
    assert result["status"] == "NOT_ANALYZED_NO_MODEL_INVOKED"
