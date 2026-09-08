"""
GeoTIFF Reader
"""

from pathlib import Path

from acf.importers.base.base_reader import BaseReader


class GeoTIFFReader(BaseReader):
    name = "GeoTIFF Reader"
    SUPPORTED_EXTENSIONS = (".tif", ".tiff")

    def can_read(self, filename):
        return Path(filename).suffix.lower() in self.SUPPORTED_EXTENSIONS

    def read(self, filename):
        return Path(filename)
