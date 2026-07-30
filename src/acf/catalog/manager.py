"""
ACF Catalog Manager (Canonical Implementation)

Central access point for all catalogs.
"""

from acf.catalog.default_catalog import create_catalog
from acf.catalog.dataset_catalog import DatasetCatalog


class CatalogManager:
    """
    Gestionnaire global et unifié des catalogues ACF.
    """

    def __init__(self):
        self._catalogs = {}
        self._scientific = None
        self._datasets = None

    @property
    def scientific(self):
        if self._scientific is None:
            self._scientific = create_catalog()
            self._catalogs["scientific"] = self._scientific
        return self._scientific

    @property
    def datasets(self):
        if self._datasets is None:
            self._datasets = DatasetCatalog()
            self._catalogs["datasets"] = self._datasets
        return self._datasets

    def register(self, name, catalog):
        self._catalogs[name] = catalog

    def get(self, name):
        return self._catalogs.get(name)

    def exists(self, name):
        return name in self._catalogs

    def remove(self, name):
        if name in self._catalogs:
            del self._catalogs[name]
        if name == "scientific":
            self._scientific = None
        if name == "datasets":
            self._datasets = None

    def clear(self):
        self._catalogs.clear()
        self._scientific = None
        self._datasets = None

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

    def add_dataset(self, entry):
        self.datasets.add(entry)

    def dataset_count(self):
        return self.datasets.count()

    def parameters(self):
        return self.scientific.all()

    def datasets_list(self):
        return self.datasets.all()

    def status(self):
        return {
            "scientific_parameters": len(self.scientific.all()),
            "datasets": self.datasets.count(),
        }
