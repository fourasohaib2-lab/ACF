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


def __getattr__(name):
    if name == "ParameterSearch":
        from acf.parameters.search import ParameterSearch
        return ParameterSearch
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
