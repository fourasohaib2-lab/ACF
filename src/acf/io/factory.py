class ReaderFactory:

    def __init__(self, registry):

        self.registry = registry

    def get_reader(self, filename):

        for reader in self.registry.readers():

            if reader.can_read(filename):
                return reader

        return None
