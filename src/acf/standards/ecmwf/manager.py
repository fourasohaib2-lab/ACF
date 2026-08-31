"""
ECMWF Manager
"""

from acf.standards.ecmwf.converter import ECMWFConverter
from acf.standards.ecmwf.loader import ECMWFLoader


class ECMWFManager:
    def __init__(self):

        self.loader = ECMWFLoader()
        self.converter = ECMWFConverter()

    def load(self, filename):

        data = self.loader.load(filename)

        parameters = []

        for code, values in data.items():
            parameters.append(self.converter.convert(code, values))

        return parameters
