"""
Atmospheric Complexity Framework (ACF)

CATALOG - Catalog

Purpose:
--------
Provides parameter and dataset cataloging, indexing, and search capabilities.

Responsibilities:
-----------------
• Manage catalog logic and state representations.
• Integrate with the catalog subsystem of the ACF scientific engine.

Major Components:
-----------------
• ScientificCatalog

Dependencies:
-------------
• Python Standard Library and NumPy/Scientific Python Stack.
• Internal acf.catalog module infrastructure.

Scientific Context:
-------------------
Provides foundational capabilities for numerical weather prediction, atmospheric data processing,
physical modeling, and spatial-temporal analysis within the Atmospheric Complexity Framework.
"""

from acf.catalog.catalog_entry import CatalogEntry


class ScientificCatalog:

    def __init__(self):

        self.entries = {}

    ##########################################

    def register(self, entry: CatalogEntry):

        self.entries[entry.parameter_id] = entry

    ##########################################

    def get(self, parameter_id):

        return self.entries.get(parameter_id)

    ##########################################

    def exists(self, parameter_id):

        return parameter_id in self.entries

    ##########################################

    def all(self):

        return list(self.entries.values())

    ##########################################

    def by_category(self, category):

        return [
            e
            for e in self.entries.values()
            if e.category == category
        ]
