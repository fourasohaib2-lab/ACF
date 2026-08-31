"""
Automatic Model Detector
"""


class ModelDetector:
    def __init__(self, registry):

        self.registry = registry

    def detect(self, dataset):

        for model_name in self.registry.list_models():
            model = self.registry.get(model_name)

            if model.detect(dataset):
                return model

        return None
