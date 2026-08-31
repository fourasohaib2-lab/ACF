"""
Atmospheric Complexity Framework (ACF)

BUFR Adapter
"""

from pathlib import Path

from acf.data.dataset import Dataset


class BUFRAdapter:
    supported_extensions = [
        ".bufr",
        ".buf",
        ".bfr",
    ]

    def __init__(self):

        self.filename = None

    def open(self, filename):

        self.filename = Path(filename)

        return self.filename

    @property
    def exists(self):

        return self.filename is not None and self.filename.exists()

    @property
    def suffix(self):

        if self.filename is None:
            return ""

        return self.filename.suffix.lower()

    def is_bufr(self):

        return self.suffix in self.supported_extensions

    def supports(self, filepath):

        return Path(filepath).suffix.lower() in self.supported_extensions

    def load(self, filepath):

        filepath = Path(filepath)

        return Dataset(
            name=filepath.stem,
            filepath=filepath,
            filetype="BUFR",
        )
