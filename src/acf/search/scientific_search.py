"""
Scientific Search Engine
"""

from acf.catalogs.hub import CatalogHub


class ScientificSearch:

    def __init__(self):

        self.hub = CatalogHub()

    def initialize(self):

        self.hub.load_cf()

    def find(self, key):

        return self.hub.find(key)

    def search(self, text):

        return self.hub.search(text)
