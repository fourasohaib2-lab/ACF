"""
Atmospheric Complexity Framework (ACF)

XML Adapter
"""

from pathlib import Path

from acf.data.dataset import Dataset


class XMLAdapter:
    """
    Adapter for XML datasets.
    """

    supported_extensions = [".xml"]

    def load(self, filepath: Path):

        return Dataset(
            name=filepath.stem,
            filepath=filepath,
            filetype="XML",
        )

    def supports(self, filepath: Path):

        return filepath.suffix.lower() in self.supported_extensions
