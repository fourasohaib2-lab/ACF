"""
Atmospheric Complexity Framework (ACF)

IMPORTERS - Registry

Purpose:
--------
Reader and Importer registry.
"""


class ReaderRegistry:
    def __init__(self):
        self._readers = []

    def register(self, reader):
        self._readers.append(reader)

    def readers(self):
        return list(self._readers)

    def count(self):
        return len(self._readers)
