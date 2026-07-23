"""
Base Importer
"""

from abc import ABC, abstractmethod


class BaseImporter(ABC):

    @abstractmethod
    def load(self, filename):
        """Charge un catalogue."""
        raise NotImplementedError

    @abstractmethod
    def validate(self, filename):
        """Valide un fichier."""
        raise NotImplementedError

