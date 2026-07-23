"""
WMO Importer
"""

from pathlib import Path

from acf.importers.base.base_importer import BaseImporter


class WMOImporter(BaseImporter):

    def validate(self, filename):

        return Path(filename).exists()

    def load(self, filename):

        filename = Path(filename)

        if not self.validate(filename):
            raise FileNotFoundError(filename)

        return filename.read_text(encoding="utf-8")
