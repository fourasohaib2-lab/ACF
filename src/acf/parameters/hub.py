"""
Universal Parameter Hub
"""

from acf.parameters.aliases import ParameterAliases
from acf.parameters.index import ParameterIndex
from acf.parameters.parameter import Parameter
from acf.parameters.registry import ParameterRegistry
from acf.parameters.search import ParameterSearch


class ParameterHub:
    def __init__(self):

        self.registry = ParameterRegistry()
        self.search = ParameterSearch(self.registry)
        self.aliases = ParameterAliases()
        self.index = ParameterIndex()

    def register(self, parameter: Parameter):

        self.registry.register(parameter)
        self.index.add(parameter)

    def add_alias(self, alias, code):

        self.aliases.add(alias, code)
        self.search.aliases.add(alias, code)

    def by_code(self, code):

        parameter = self.index.by_code(code)

        if parameter is not None:
            return parameter

        return self.search.by_code(code)

    def by_name(self, name):

        parameter = self.index.by_name(name)

        if parameter is not None:
            return parameter

        return self.search.by_name(name)

    def by_alias(self, alias):

        return self.search.by_alias(alias)

    def exists(self, code):

        return self.registry.exists(code)

    def count(self):

        return self.registry.count()
