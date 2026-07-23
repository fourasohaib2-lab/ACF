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
