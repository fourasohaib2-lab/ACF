"""
Parameter Alias Manager
"""


class ParameterAliases:

    def __init__(self):

        self._aliases = {}

    def add(self, alias, code):

        self._aliases[alias.lower()] = code

    def resolve(self, alias):

        return self._aliases.get(alias.lower())

    def exists(self, alias):

        return alias.lower() in self._aliases

    def count(self):

        return len(self._aliases)

    def aliases(self):

        return sorted(self._aliases.keys())
"""
Parameter Search Engine
"""

from acf.parameters.registry import ParameterRegistry
from acf.parameters.aliases import ParameterAliases


class ParameterSearch:

    def __init__(self, registry: ParameterRegistry):

        self.registry = registry
        self.aliases = ParameterAliases()

    def by_code(self, code):

        return self.registry.get(code)

    def by_alias(self, alias):

        code = self.aliases.resolve(alias)

        if code is None:
            return None

        return self.registry.get(code)

    def by_name(self, name):

        name = name.lower()

        for parameter in self.registry._parameters.values():

            if parameter.name.lower() == name:

                return parameter

        return None

    def exists(self, code):

        return self.registry.exists(code)

    def all_codes(self):

        return self.registry.list_codes()
