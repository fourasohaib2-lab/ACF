"""
Atmospheric Complexity Framework (ACF)

PARAMETERS - Catalog

Purpose:
--------
Physical parameter definitions, unit conversion tables, and parameter aliases.

Responsibilities:
-----------------
• Manage catalog logic and state representations.
• Integrate with the parameters subsystem of the ACF scientific engine.

Major Components:
-----------------
• ParameterCatalog

Dependencies:
-------------
• Python Standard Library and NumPy/Scientific Python Stack.
• Internal acf.parameters module infrastructure.

Scientific Context:
-------------------
Provides foundational capabilities for numerical weather prediction, atmospheric data processing,
physical modeling, and spatial-temporal analysis within the Atmospheric Complexity Framework.
"""

from acf.parameters.parameter import Parameter


class ParameterCatalog:

    def __init__(self):

        self.parameters = {}

    def register(self, parameter):

        self.parameters[parameter.code] = parameter

    def get(self, code):

        return self.parameters.get(code)

    def exists(self, code):

        return code in self.parameters

    def list_codes(self):

        return sorted(self.parameters.keys())

    def __len__(self):

        return len(self.parameters)
