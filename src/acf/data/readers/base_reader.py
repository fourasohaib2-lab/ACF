"""
ACF Base Reader

Common interface for scientific data readers.
"""


from abc import ABC, abstractmethod



class BaseReader(ABC):
    """
    Interface commune des lecteurs ACF.
    """



    name = "Base Reader"



    ##################################################

    @abstractmethod
    def can_read(self, filename):

        """
        Vérifie si le lecteur accepte le fichier.
        """

        pass



    ##################################################

    @abstractmethod
    def read(self, filename):

        """
        Charge un fichier et retourne un Dataset ACF.
        """

        pass



    ##################################################

    def info(self):

        return {

            "reader": self.__class__.__name__,

            "name": self.name,

        }
