"""
Atmospheric Complexity Framework (ACF)

CATALOG - Catalog Entry

Purpose:
--------
Provides parameter and dataset cataloging, indexing, and search capabilities.

Responsibilities:
-----------------
• Manage catalog entry logic and state representations.
• Integrate with the catalog subsystem of the ACF scientific engine.

Major Components:
-----------------
• CatalogEntry

Dependencies:
-------------
• Python Standard Library and NumPy/Scientific Python Stack.
• Internal acf.catalog module infrastructure.

Scientific Context:
-------------------
Provides foundational capabilities for numerical weather prediction, atmospheric data processing,
physical modeling, and spatial-temporal analysis within the Atmospheric Complexity Framework.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class CatalogEntry:

    parameter_id: str

    standard_name: str

    long_name: str

    units: str

    category: str

    level_type: str

    renderer: str

    colormap: str

    grib_code: str = ""

    cf_name: str = ""

    description: str = ""
