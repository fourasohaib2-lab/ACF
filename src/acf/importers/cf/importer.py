"""
CF Importer
"""

import json
from pathlib import Path

from acf.importers.base.base_importer import BaseImporter


class CFImporter(BaseImporter):
    def validate(self, filename):

        return Path(filename).exists()

    def load(self, filename):

        filename = Path(filename)

        if not self.validate(filename):
            raise FileNotFoundError(filename)

        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
