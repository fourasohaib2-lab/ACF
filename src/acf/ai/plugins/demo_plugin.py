"""
Demo AI Plugin
"""

from acf.ai.plugins.base_plugin import AIPlugin


class DemoPlugin(AIPlugin):

    def __init__(self):

        super().__init__("demo")

    def analyze(self, dataset):

        return {
            "plugin": self.name,
            "status": "ok",
            "variables": list(dataset.keys())
            if isinstance(dataset, dict)
            else []
        }
