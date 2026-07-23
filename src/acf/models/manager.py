"""
Weather Model Manager
"""

from acf.models.detector import ModelDetector
from acf.models.registry import ModelRegistry
from acf.models.implementations.era5 import ERA5Model


class ModelManager:

    def __init__(self):

        self.registry = ModelRegistry()

        self._load_builtin_models()

        self.detector = ModelDetector(self.registry)

    def _load_builtin_models(self):

        self.registry.register(ERA5Model())

    def register(self, model):

        self.registry.register(model)

    def detect(self, dataset):

        return self.detector.detect(dataset)

    def models(self):

        return self.registry.list_models()
