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
