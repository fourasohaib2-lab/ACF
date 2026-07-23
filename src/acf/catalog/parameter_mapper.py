class ParameterMapper:

    def __init__(self):

        self.aliases = {}

    ##################################################

    def register(self, canonical_name, *aliases):

        canonical = canonical_name.lower()

        self.aliases[canonical] = canonical

        for alias in aliases:
            self.aliases[alias.lower()] = canonical

    ##################################################

    def resolve(self, variable):

        if variable is None:
            return None

        return self.aliases.get(variable.lower())

    ##################################################

    def exists(self, variable):

        return self.resolve(variable) is not None

    ##################################################

    def all_aliases(self):

        return dict(self.aliases)
