"""
Atmospheric Complexity Framework (ACF)

IMPORTERS - Base Reader

Purpose:
--------
Common interface for data and catalog readers/importers.
"""

from abc import ABC, abstractmethod


class BaseReader(ABC):
    """
    Interface commune des lecteurs de données ACF.
    """

    name = "Base Reader"
    extensions = []

    @abstractmethod
    def can_read(self, filename: str) -> bool:
        """Vérifie si le lecteur accepte le fichier."""
        pass

    @abstractmethod
    def read(self, filename: str):
        """Charge un fichier et retourne un Dataset ou des données ACF."""
        pass

    def info(self):
        return {
            "reader": self.__class__.__name__,
            "name": self.name,
        }
