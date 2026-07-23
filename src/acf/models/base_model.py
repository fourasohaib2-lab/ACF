"""
Base Weather Model
"""

from abc import ABC
from abc import abstractmethod


class BaseWeatherModel(ABC):

    name = "Unknown"

    supported_extensions = ()

    @abstractmethod
    def detect(self, dataset):
        pass

    @abstractmethod
    def variables(self):
        pass

    @abstractmethod
    def levels(self):
        pass

    @abstractmethod
    def projection(self):
        pass
