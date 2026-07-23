"""
Parameter Registry
"""

from acf.parameters.parameter import Parameter


class ParameterRegistry:

    def __init__(self):

        self._parameters = {}

    def register(self, parameter: Parameter):

        self._parameters[parameter.code] = parameter

    def unregister(self, code):

        self._parameters.pop(code, None)

    def exists(self, code):

        return code in self._parameters

    def get(self, code):

        return self._parameters.get(code)

    def list_codes(self):

        return sorted(self._parameters.keys())

    def count(self):

        return len(self._parameters)

    def clear(self):

        self._parameters.clear()

