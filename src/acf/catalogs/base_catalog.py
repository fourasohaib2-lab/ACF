"""
Base Catalog
"""

from abc import ABC, abstractmethod


class BaseCatalog(ABC):

    @abstractmethod
    def load(self):
        """Charge le catalogue."""
        raise NotImplementedError

    @abstractmethod
    def count(self):
        """Retourne le nombre d'éléments."""
        raise NotImplementedError

