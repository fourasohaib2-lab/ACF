"""
Base class for AI plugins.
"""

from abc import ABC, abstractmethod


class AIPlugin(ABC):

    def __init__(self, name):

        self.name = name

    @abstractmethod
    def analyze(self, dataset):

        pass
