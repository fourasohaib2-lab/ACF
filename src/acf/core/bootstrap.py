"""
Bootstrap
"""

from acf.core.config import ConfigManager
from acf.core.logger import get_logger
from acf.core.plugin_manager import PluginManager
from acf.core.service_manager import ServiceManager


class Bootstrap:

    def __init__(self):
        self.logger = get_logger()
        self.config = ConfigManager()
        self.plugins = PluginManager()
        self.services = ServiceManager()

    def initialize(self):

        self.logger.info("Loading configuration...")
        self.config.load()

        self.logger.info("Registering services...")
        self.services.register("logger", self.logger)
        self.services.register("config", self.config)
        self.services.register("plugins", self.plugins)

        self.logger.info("Searching plugins...")
        self.plugins.discover()

        self.logger.info("Starting services...")

        self.logger.success("ACF is ready.")
