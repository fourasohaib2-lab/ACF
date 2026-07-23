"""
Standards Hub
"""

from acf.standards.manager import StandardsManager
from acf.standards.ecmwf.manager import ECMWFManager


class StandardsHub:

    def __init__(self):

        self.manager = StandardsManager()
        self.cf = self.manager
        self.ecmwf = ECMWFManager()

    # ----- API générique -----

    def register(self, name, standard):
        self.manager.register(name, standard)

    def get(self, name):
        return self.manager.get(name)

    def exists(self, name):
        return self.manager.exists(name)

    def names(self):
        return self.manager.names()

    def count(self):
        return self.manager.count()

    # ----- API existante -----

    def load_ecmwf(self, filename):
        return self.ecmwf.load(filename)

    def get_cf(self, standard_name):
        return self.manager.get_cf(standard_name)

    def exists_cf(self, standard_name):
        return self.manager.exists_cf(standard_name)
