"""
Plugin Manager
"""

from acf.ai.plugins.base_plugin import AIPlugin


class PluginManager:
    def __init__(self):

        self.plugins = {}

    ##################################################

    def register(self, plugin: AIPlugin):

        self.plugins[plugin.name] = plugin

    ##################################################

    def available(self):

        return sorted(self.plugins.keys())

    ##################################################

    def get(self, name):

        return self.plugins.get(name)

    ##################################################

    def analyze(self, plugin_name, dataset):

        plugin = self.get(plugin_name)

        if plugin is None:
            raise ValueError(f"Plugin '{plugin_name}' not found.")

        return plugin.analyze(dataset)
