"""
Parameter Index
"""

from acf.parameters.parameter import Parameter


class ParameterIndex:

    def __init__(self):

        self._code_index = {}
        self._name_index = {}

    def add(self, parameter: Parameter):

        self._code_index[parameter.code.lower()] = parameter

        self._name_index[parameter.name.lower()] = parameter

    def by_code(self, code):

        return self._code_index.get(code.lower())

    def by_name(self, name):

        return self._name_index.get(name.lower())

    def exists(self, code):

        return code.lower() in self._code_index

    def count(self):

        return len(self._code_index)

    def clear(self):

        self._code_index.clear()
        self._name_index.clear()
