"""
ECMWF Catalog
"""

from acf.catalogs.base_catalog import BaseCatalog
from acf.standards.ecmwf.manager import ECMWFManager


class ECMWFCatalog(BaseCatalog):
    def __init__(self):

        self.manager = ECMWFManager()
        self._parameters = {}

    def load(self, filename):

        parameters = self.manager.load(filename)

        self._parameters = {}

        for parameter in parameters:
            self._parameters[parameter.code] = parameter

    def count(self):

        return len(self._parameters)

    def exists(self, code):

        return code in self._parameters

    def get(self, code):

        return self._parameters.get(code)

    def list(self):

        return sorted(self._parameters.keys())
