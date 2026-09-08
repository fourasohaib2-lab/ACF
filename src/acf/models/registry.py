"""
Model Registry
"""


class ModelRegistry:
    def __init__(self):
        self._models = {}

    def register(self, model):
        self._models[model.name] = model

    def unregister(self, name):
        self._models.pop(name, None)

    def get(self, name):
        return self._models.get(name)

    def exists(self, name):
        return name in self._models

    def list_models(self):
        return list(self._models.keys())

    def __len__(self):
        return len(self._models)
