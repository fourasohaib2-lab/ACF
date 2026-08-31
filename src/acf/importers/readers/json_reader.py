"""
JSON Reader
"""

import json
from pathlib import Path

from acf.importers.base.base_reader import BaseReader


class JSONReader(BaseReader):
    name = "JSON Reader"
    SUPPORTED_EXTENSIONS = (".json",)

    def can_read(self, filename):
        return Path(filename).suffix.lower() in self.SUPPORTED_EXTENSIONS

    def read(self, filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
