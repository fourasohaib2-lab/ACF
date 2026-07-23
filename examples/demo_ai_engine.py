from acf.ai.engine import AIEngine

engine = AIEngine()

engine.register_model("forecast", object())

print("Models :", engine.available_models())

result = engine.analyze({"temperature": 30})

print(result)
