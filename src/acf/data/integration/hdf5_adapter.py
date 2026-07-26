"""
Atmospheric Complexity Framework (ACF)

HDF5 Adapter
"""

from pathlib import Path

from acf.data.dataset import Dataset


class HDF5Adapter:
    """
    Adapter for HDF5 datasets.
    """

    supported_extensions = [".h5", ".hdf5"]

    def load(self, filepath: Path):

        return Dataset(
            name=filepath.stem,
            filepath=filepath,
            filetype="HDF5",
        )

    def supports(self, filepath: Path):

        return filepath.suffix.lower() in self.supported_extensions
