#!/usr/bin/env bash

set -e

PROJECT="/home/souhaib/ACF"

echo "======================================="
echo " ACF Sprint 09 - Partie 2"
echo " AI Plugin System"
echo "======================================="

mkdir -p "$PROJECT/src/acf/ai/plugins"

touch "$PROJECT/src/acf/ai/plugins/__init__.py"

####################################################
# PLUGIN BASE
####################################################

cat > "$PROJECT/src/acf/ai/plugins/base_plugin.py" << 'EOF'
"""
Base class for AI plugins.
"""

from abc import ABC, abstractmethod


class AIPlugin(ABC):

    def __init__(self, name):

        self.name = name

    @abstractmethod
    def analyze(self, dataset):

        pass
EOF

####################################################
# PLUGIN MANAGER
####################################################

cat > "$PROJECT/src/acf/ai/plugins/plugin_manager.py" << 'EOF'
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
            raise ValueError(
                f"Plugin '{plugin_name}' not found."
            )

        return plugin.analyze(dataset)
EOF

####################################################
# DEMO PLUGIN
####################################################

cat > "$PROJECT/src/acf/ai/plugins/demo_plugin.py" << 'EOF'
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
EOF

####################################################
# TESTS
####################################################

cat > "$PROJECT/tests/test_ai_plugin_manager.py" << 'EOF'
from acf.ai.plugins.plugin_manager import PluginManager
from acf.ai.plugins.demo_plugin import DemoPlugin


def test_plugin_registration():

    manager = PluginManager()

    plugin = DemoPlugin()

    manager.register(plugin)

    assert "demo" in manager.available()


def test_plugin_execution():

    manager = PluginManager()

    manager.register(DemoPlugin())

    result = manager.analyze(
        "demo",
        {
            "temperature": 25,
            "pressure": 1015
        }
    )

    assert result["status"] == "ok"

    assert "temperature" in result["variables"]
EOF

####################################################
# EXAMPLE
####################################################

mkdir -p "$PROJECT/examples"

cat > "$PROJECT/examples/demo_ai_plugin.py" << 'EOF'
from acf.ai.plugins.plugin_manager import PluginManager
from acf.ai.plugins.demo_plugin import DemoPlugin

manager = PluginManager()

manager.register(DemoPlugin())

print("Available plugins:")

print(manager.available())

result = manager.analyze(
    "demo",
    {
        "temperature": 31,
        "humidity": 60,
        "wind": 18
    }
)

print(result)
EOF

echo
echo "AI Plugin System installed successfully."
