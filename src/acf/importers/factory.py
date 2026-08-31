"""
Atmospheric Complexity Framework (ACF)

IMPORTERS - Factory

Purpose:
--------
Unified Reader & Importer Factory supporting both dynamic discovery and explicit registry.
"""

import importlib
import inspect
import pkgutil


class ReaderFactory:
    def __init__(self, registry=None):
        self._readers = []
        if registry is not None:
            self.registry = registry
            for reader in registry.readers():
                self.register(reader)
        else:
            self.registry = None
            self.discover()

    def discover(self):
        """
        Recherche automatiquement tous les lecteurs.
        """
        self._readers = []
        try:
            import acf.importers.readers as importers_readers_package

            self._discover_in_package(importers_readers_package, "acf.importers.readers")
        except Exception:
            pass

        try:
            import acf.data.readers as data_readers_package

            self._discover_in_package(data_readers_package, "acf.data.readers")
        except Exception:
            pass

    def _discover_in_package(self, package, package_name):
        registered_classes = {r.__class__ for r in self._readers}
        for _, module_name, _ in pkgutil.iter_modules(package.__path__):
            try:
                module = importlib.import_module(f"{package_name}.{module_name}")
            except Exception:
                continue

            for _, cls in inspect.getmembers(module, inspect.isclass):
                if cls.__module__ != module.__name__:
                    continue

                if (
                    cls.__name__.endswith("Reader")
                    and cls.__name__ not in ("BaseReader", "Reader")
                    and cls not in registered_classes
                ):
                    try:
                        instance = cls()
                        self.register(instance)
                        registered_classes.add(cls)
                    except Exception:
                        pass

    def register(self, reader):
        if reader not in self._readers:
            self._readers.append(reader)

    def readers(self):
        if self.registry is not None:
            return self.registry.readers()
        return list(self._readers)

    def get_reader(self, filename):
        for reader in self.readers():
            if hasattr(reader, "can_read") and reader.can_read(filename):
                return reader
        return None
