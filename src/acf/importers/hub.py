"""
Importer Hub
"""

from acf.importers.manager import ImporterManager


class ImporterHub:

    def __init__(self):

        self.manager = ImporterManager()

    def get(self, name):

        return self.manager.get(name)

    def exists(self, name):

        return self.manager.exists(name)

    def names(self):

        return self.manager.names()

    def load(self, importer_name, filename):

        importer = self.get(importer_name)

        if importer is None:
            raise ValueError(f"Unknown importer: {importer_name}")

        return importer.load(filename)
    def auto_load(self, filename):

        importer = self.manager.detect_importer(filename)

        if importer is None:
            raise ValueError(f"No importer found for {filename}")

        return importer.load(filename)
