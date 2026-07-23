"""
Standards Manager
"""

from acf.standards.cf_standard_names import CF_STANDARD_NAMES


class StandardsManager:

    def __init__(self):

        self.cf = CF_STANDARD_NAMES
        self._standards = {}

    def register(self, name, standard):
        self._standards[name] = standard

    def get(self, name):
        return self._standards.get(name)

    def exists(self, name):
        return name in self._standards

    def names(self):
        return sorted(self._standards.keys())

    def count(self):
        return len(self._standards)

    def get_cf(self, standard_name):
        return self.cf.get(standard_name)

    def exists_cf(self, standard_name):
        return standard_name in self.cf

    def list_cf(self):
        return sorted(self.cf.keys())

    def count_cf(self):
        return len(self.cf)
