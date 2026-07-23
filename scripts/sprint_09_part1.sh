#!/usr/bin/env bash

set -e

PROJECT="/home/souhaib/ACF"

echo "======================================="
echo " ACF Sprint 09 - Partie 1"
echo " AI Engine"
echo "======================================="

####################################################
# DOSSIERS
####################################################

mkdir -p "$PROJECT/src/acf/ai"

touch "$PROJECT/src/acf/ai/__init__.py"

####################################################
# AI ENGINE
####################################################

cat > "$PROJECT/src/acf/ai/engine.py" << 'EOF'
"""
Artificial Intelligence Engine
"""

from datetime import datetime


class AIEngine:
    """
    Cœur du moteur IA d'ACF.
    """

    def __init__(self):

        self.version = "0.1.0"

        self.loaded_models = {}

        self.history = []

    ##################################################

    def register_model(self, name, model):

        self.loaded_models[name] = model

    ##################################################

    def available_models(self):

        return sorted(self.loaded_models.keys())

    ##################################################

    def analyze(self, dataset):

        result = {
            "timestamp": datetime.utcnow(),
            "status": "success",
            "dataset": str(type(dataset).__name__)
        }

        self.history.append(result)

        return result

    ##################################################

    def history_count(self):

        return len(self.history)

    ##################################################

    def clear_history(self):

        self.history.clear()
EOF

####################################################
# TESTS
####################################################

cat > "$PROJECT/tests/test_ai_engine.py" << 'EOF'
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
EOF

####################################################
# EXEMPLE
####################################################

mkdir -p "$PROJECT/examples"

cat > "$PROJECT/examples/demo_ai_engine.py" << 'EOF'
from acf.ai.engine import AIEngine

engine = AIEngine()

engine.register_model("forecast", object())

print("Models :", engine.available_models())

result = engine.analyze({"temperature": 30})

print(result)
EOF

echo
echo "AI Engine installed successfully."

