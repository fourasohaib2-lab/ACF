"""
Atmospheric Complexity Framework (ACF)

JSON Adapter
"""

from pathlib import Path

from acf.data.dataset import Dataset


class JSONAdapter:
    """
    Adapter for JSON datasets.
    """

    supported_extensions = [".json"]

    def load(self, filepath: Path):

        return Dataset(
            name=filepath.stem,
            filepath=filepath,
            filetype="JSON",
        )

    def supports(self, filepath: Path):

        return filepath.suffix.lower() in self.supported_extensions
