"""
Importer Manager
"""

from acf.importers.cf.importer import CFImporter
from acf.importers.ecmwf.importer import ECMWFImporter
from acf.importers.wmo.importer import WMOImporter


class ImporterManager:

    def __init__(self):

        self._importers = {}

        self.register("cf", CFImporter())
        self.register("ecmwf", ECMWFImporter())
        self.register("wmo", WMOImporter())

    def register(self, name, importer):

        self._importers[name] = importer

    def get(self, name):

        return self._importers.get(name)

    def exists(self, name):

        return name in self._importers

    def names(self):

        return sorted(self._importers.keys())
    def detect_importer(self, filename):

        filename = str(filename).lower()

        if "cf" in filename:
            return self.get("cf")

        if "ecmwf" in filename:
            return self.get("ecmwf")

        if "wmo" in filename:
            return self.get("wmo")

        return None
