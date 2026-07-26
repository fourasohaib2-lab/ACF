"""
Atmospheric Complexity Framework (ACF)

CSV Adapter
"""

from pathlib import Path

from acf.data.dataset import Dataset


class CSVAdapter:
    """
    Adapter for CSV datasets.
    """

    supported_extensions = [".csv"]

    def load(self, filepath: Path):

        return Dataset(
            name=filepath.stem,
            filepath=filepath,
            filetype="CSV",
        )

    def supports(self, filepath: Path):

        return filepath.suffix.lower() in self.supported_extensions
