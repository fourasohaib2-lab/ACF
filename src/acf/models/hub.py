"""
Weather Model Hub
"""

from acf.models.manager import ModelManager


class ModelHub:

    def __init__(self):

        self.manager = ModelManager()

    def available_models(self):

        return self.manager.models()

    def count(self):

        return len(self.available_models())

    def has_model(self, name):

        return name in self.available_models()

