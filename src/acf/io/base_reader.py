from abc import ABC, abstractmethod


class BaseReader(ABC):

    extensions = []

    @abstractmethod
    def can_read(self, filename: str) -> bool:
        pass

    @abstractmethod
    def read(self, filename: str):
        pass
