"""
Scientific Data Manager
"""

from acf.data.factory import ReaderFactory


class DataManager:

    def __init__(self):

        self.factory = ReaderFactory()

    def available_readers(self):

        return [
            reader.__class__.__name__
            for reader in self.factory.readers()
        ]

    def open(self, filename):

        reader = self.factory.get_reader(filename)

        if reader is None:

            raise ValueError(
                f"No reader available for '{filename}'."
            )

        return reader.read(filename)
