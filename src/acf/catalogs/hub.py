"""
Catalog Hub
"""

from acf.catalogs.catalog_manager import CatalogManager
from acf.catalogs.cf.catalog import CFCatalog
from acf.catalogs.ecmwf.catalog import ECMWFCatalog


class CatalogHub:

    def __init__(self):

        self.manager = CatalogManager()

    def load_cf(self):

        catalog = CFCatalog()
        catalog.load()

        self.manager.register("cf", catalog)

    def load_ecmwf(self, filename):

        catalog = ECMWFCatalog()
        catalog.load(filename)

        self.manager.register("ecmwf", catalog)

    def find(self, key):

        return self.manager.find(key)

    def search(self, text):

        return self.manager.search(text)

    def list_catalogs(self):

        return self.manager.list_catalogs()
