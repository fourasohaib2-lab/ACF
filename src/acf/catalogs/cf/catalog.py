"""
CF Catalog
"""

from acf.catalogs.base_catalog import BaseCatalog
from acf.standards.cf_standard_names import CF_STANDARD_NAMES


class CFCatalog(BaseCatalog):
    def __init__(self):

        self._parameters = {}

    def load(self):

        self._parameters = dict(CF_STANDARD_NAMES)

    def count(self):

        return len(self._parameters)

    def exists(self, standard_name):

        return standard_name in self._parameters

    def get(self, standard_name):

        return self._parameters.get(standard_name)

    def list(self):

        return sorted(self._parameters.keys())
