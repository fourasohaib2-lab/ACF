"""
Universal Catalog Manager
"""


class CatalogManager:

    def __init__(self):

        self._catalogs = {}

    def register(self, name, catalog):

        self._catalogs[name] = catalog

    def get(self, name):

        return self._catalogs.get(name)

    def exists(self, name):

        return name in self._catalogs

    def remove(self, name):

        if name in self._catalogs:
            del self._catalogs[name]

    def clear(self):

        self._catalogs.clear()

    def count(self):

        return len(self._catalogs)

    def names(self):

        return sorted(self._catalogs.keys())

    def list_catalogs(self):

        return sorted(self._catalogs.keys())
    def find(self, key):

        for catalog in self._catalogs.values():

            if hasattr(catalog, "exists") and catalog.exists(key):
                return catalog.get(key)

        return None
    def search(self, text):

        text = text.lower()

        results = []

        for catalog in self._catalogs.values():

            if hasattr(catalog, "list"):

                for key in catalog.list():

                    if text in key.lower():

                        results.append(catalog.get(key))

        return results
