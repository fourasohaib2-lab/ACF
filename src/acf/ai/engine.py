"""
Artificial Intelligence Engine
"""

from datetime import UTC, datetime


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
        """
        NOTE (correction): this used to unconditionally report
        "status": "success" regardless of what dataset was passed -
        no analysis is actually performed here at all (self.loaded_models
        is never consulted, dataset's contents are never inspected
        beyond its type name). A caller could believe a real AI
        analysis had run and succeeded when nothing was analyzed.
        Honestly reports that instead.
        """
        result = {
            "timestamp": datetime.now(UTC),
            "status": "NOT_ANALYZED_NO_MODEL_INVOKED",
            "dataset": str(type(dataset).__name__),
        }

        self.history.append(result)

        return result

    ##################################################

    def history_count(self):

        return len(self.history)

    ##################################################

    def clear_history(self):

        self.history.clear()
