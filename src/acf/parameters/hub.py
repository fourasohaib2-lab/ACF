"""
Universal Parameter Hub
"""

from acf.parameters.index import ParameterIndex
from acf.parameters.parameter import Parameter
from acf.parameters.registry import ParameterRegistry
from acf.parameters.search import ParameterSearch


class ParameterHub:
    def __init__(self):

        self.registry = ParameterRegistry()
        self.search = ParameterSearch(self.registry)
        self.index = ParameterIndex()

    def register(self, parameter: Parameter):

        self.registry.register(parameter)
        self.index.add(parameter)

    def add_alias(self, alias, code):
        """
        NOTE (correction): this used to also write to a second,
        separate ParameterHub.aliases store (self.aliases =
        ParameterAliases()) that nothing ever read (by_alias() only
        ever consulted self.search.aliases) - dead state kept "in
        sync" by writing twice, which would have silently diverged
        from the real one had any code ever written to self.aliases
        directly instead of through add_alias(). Removed the unused
        duplicate; self.search.aliases is the single source of truth.
        """
        self.search.aliases.add(alias, code)

    @property
    def aliases(self):
        """Backward-compatible read access to the single alias store (see add_alias's NOTE)."""
        return self.search.aliases

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
