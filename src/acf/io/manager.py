from acf.io.factory import ReaderFactory


class DataManager:

    def __init__(self, registry):

        self.factory = ReaderFactory(registry)

    def open(self, filename):

        reader = self.factory.get_reader(filename)

        if reader is None:
            raise ValueError(f"No reader available for {filename}")

        return reader.read(filename)
