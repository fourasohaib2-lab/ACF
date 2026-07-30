"""
BUFR Reader
"""

from pathlib import Path


class BufrReader:
    """Simple BUFR reader."""

    def __init__(self, filename=None):
        self.filename = filename
        self.file = None
        self.is_open = False

    def open(self, filename=None):
        if filename is not None:
            self.filename = filename

        if self.filename is None:
            raise ValueError("No BUFR file specified.")

        self.file = Path(self.filename)
        self.is_open = True

    def close(self):
        self.file = None
        self.is_open = False

    def exists(self):
        if self.filename is None:
            return False
        return Path(self.filename).exists()

    def variables(self):
        return []

    def coordinates(self):
        return []

    def attributes(self):
        return {}

    def stations(self):
        return []

    def times(self):
        return []

    def messages(self):
        return 0

    def __repr__(self):
        return f"BufrReader(open={self.is_open})"
