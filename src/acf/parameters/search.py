"""
Parameter Search Engine
"""

from acf.parameters.aliases import ParameterAliases
from acf.parameters.registry import ParameterRegistry


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
