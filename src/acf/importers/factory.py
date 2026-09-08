"""
Atmospheric Complexity Framework (ACF)

IMPORTERS - Factory

Purpose:
--------
Unified Reader & Importer Factory supporting both dynamic discovery and explicit registry.
"""

import importlib
import inspect
import logging
import pkgutil

logger = logging.getLogger("acf.importers.factory")


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
            # NOTE (correction): a broken import of the whole readers package
            # itself (not one reader module, but the package - e.g. a bad
            # __init__.py) used to vanish silently: every get_reader() call
            # afterwards would just return None, indistinguishable from "no
            # reader supports this format" instead of "reader discovery is
            # broken". Logged now so the real cause is visible rather than
            # masquerading as an unsupported-format error downstream.
            logger.warning("ReaderFactory: acf.importers.readers package failed to import.", exc_info=True)

        try:
            import acf.data.readers as data_readers_package

            self._discover_in_package(data_readers_package, "acf.data.readers")
        except Exception:
            logger.warning("ReaderFactory: acf.data.readers package failed to import.", exc_info=True)

    def _discover_in_package(self, package, package_name):
        registered_classes = {r.__class__ for r in self._readers}
        for _, module_name, _ in pkgutil.iter_modules(package.__path__):
            full_name = f"{package_name}.{module_name}"
            try:
                module = importlib.import_module(full_name)
            except Exception:
                # A reader module failing to import here is a real bug in
                # that module (each reader already handles its own missing
                # optional dependency internally, e.g. epygram_reader.py's
                # `try: import epygram except ImportError:` guard - it never
                # raises on import) - so this is never expected to trigger
                # in a healthy environment. Logged rather than silently
                # dropped, so a future broken reader module doesn't just
                # quietly disappear from discovery.
                logger.warning("ReaderFactory: failed to import reader module '%s'.", full_name, exc_info=True)
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
                        # A reader class may legitimately raise in __init__
                        # if it requires an optional dependency that isn't
                        # available in this environment - logged at debug
                        # (not warning) since that is an expected, benign
                        # case, not a bug; still visible on demand rather
                        # than permanently invisible.
                        logger.debug(
                            "ReaderFactory: could not instantiate reader class '%s' - skipped.",
                            cls.__name__,
                            exc_info=True,
                        )

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
