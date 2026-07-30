"""
Atmospheric Complexity Framework (ACF)

CATALOG - Default Catalog

Purpose:
--------
Provides parameter and dataset cataloging, indexing, and search capabilities.

Responsibilities:
-----------------
• Manage default catalog logic and state representations.
• Integrate with the catalog subsystem of the ACF scientific engine.

Major Components:
-----------------
• Module functions and constants

Dependencies:
-------------
• Python Standard Library and NumPy/Scientific Python Stack.
• Internal acf.catalog module infrastructure.

Scientific Context:
-------------------
Provides foundational capabilities for numerical weather prediction, atmospheric data processing,
physical modeling, and spatial-temporal analysis within the Atmospheric Complexity Framework.
"""

from acf.catalog.catalog import ScientificCatalog
from acf.catalog.surface_parameters import register_surface
from acf.catalog.atmospheric_parameters import register_atmosphere
from acf.catalog.ocean_parameters import register_ocean
from acf.catalog.satellite_parameters import register_satellite
from acf.catalog.climate_parameters import register_climate


def create_catalog():

    catalog = ScientificCatalog()

    register_surface(catalog)
    register_atmosphere(catalog)
    register_ocean(catalog)
    register_satellite(catalog)
    register_climate(catalog)

    return catalog
