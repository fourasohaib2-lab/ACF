"""
CSV Reader
"""

from pathlib import Path

from acf.importers.base.base_reader import BaseReader


class CSVReader(BaseReader):
    name = "CSV Reader"
    SUPPORTED_EXTENSIONS = (".csv",)

    def can_read(self, filename):
        return Path(filename).suffix.lower() in self.SUPPORTED_EXTENSIONS

    def read(self, filename):
        return Path(filename).read_text(encoding="utf-8")
