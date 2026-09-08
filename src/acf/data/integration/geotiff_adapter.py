"""
Atmospheric Complexity Framework (ACF)

GeoTIFF Adapter
"""

from pathlib import Path

from acf.data.dataset import Dataset


class GeoTIFFAdapter:
    """
    Adapter for GeoTIFF datasets.
    """

    supported_extensions = [".tif", ".tiff"]

    def load(self, filepath: Path):

        return Dataset(
            name=filepath.stem,
            filepath=filepath,
            filetype="GeoTIFF",
        )

    def supports(self, filepath: Path):

        return filepath.suffix.lower() in self.supported_extensions
