"""
Atmospheric Complexity Framework (ACF)

CATALOG - Parameter Mapper

Purpose:
--------
Provides parameter and dataset cataloging, indexing, and search capabilities.

Responsibilities:
-----------------
• Manage parameter mapper logic and state representations.
• Integrate with the catalog subsystem of the ACF scientific engine.

Major Components:
-----------------
• ParameterMapper

Dependencies:
-------------
• Python Standard Library and NumPy/Scientific Python Stack.
• Internal acf.catalog module infrastructure.

Scientific Context:
-------------------
Provides foundational capabilities for numerical weather prediction, atmospheric data processing,
physical modeling, and spatial-temporal analysis within the Atmospheric Complexity Framework.
"""


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
