"""
Atmospheric Complexity Framework (ACF)

CATALOG - Atmospheric Parameters

Purpose:
--------
Provides parameter and dataset cataloging, indexing, and search capabilities.

Responsibilities:
-----------------
• Manage atmospheric parameters logic and state representations.
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

from acf.catalog.catalog_entry import CatalogEntry


def register_atmosphere(catalog):

    parameters = [
        CatalogEntry(
            parameter_id="t",
            standard_name="air_temperature",
            long_name="Air Temperature",
            units="K",
            category="Atmosphere",
            level_type="Pressure Level",
            renderer="Raster",
            colormap="temperature",
        ),
        CatalogEntry(
            parameter_id="q",
            standard_name="specific_humidity",
            long_name="Specific Humidity",
            units="kg kg-1",
            category="Atmosphere",
            level_type="Pressure Level",
            renderer="Raster",
            colormap="humidity",
        ),
        CatalogEntry(
            parameter_id="rh_pl",
            standard_name="relative_humidity",
            long_name="Relative Humidity",
            units="%",
            category="Atmosphere",
            level_type="Pressure Level",
            renderer="Raster",
            colormap="humidity",
        ),
        CatalogEntry(
            parameter_id="u",
            standard_name="eastward_wind",
            long_name="U Wind",
            units="m s-1",
            category="Atmosphere",
            level_type="Pressure Level",
            renderer="Wind",
            colormap="wind",
        ),
        CatalogEntry(
            parameter_id="v",
            standard_name="northward_wind",
            long_name="V Wind",
            units="m s-1",
            category="Atmosphere",
            level_type="Pressure Level",
            renderer="Wind",
            colormap="wind",
        ),
        CatalogEntry(
            parameter_id="w",
            standard_name="upward_air_velocity",
            long_name="Vertical Velocity",
            units="Pa s-1",
            category="Dynamics",
            level_type="Pressure Level",
            renderer="Raster",
            colormap="vertical_velocity",
        ),
        CatalogEntry(
            parameter_id="z",
            standard_name="geopotential",
            long_name="Geopotential",
            units="m2 s-2",
            category="Dynamics",
            level_type="Pressure Level",
            renderer="Contour",
            colormap="geopotential",
        ),
        CatalogEntry(
            parameter_id="gh",
            standard_name="geopotential_height",
            long_name="Geopotential Height",
            units="m",
            category="Dynamics",
            level_type="Pressure Level",
            renderer="Contour",
            colormap="height",
        ),
        CatalogEntry(
            parameter_id="vo",
            standard_name="atmosphere_relative_vorticity",
            long_name="Relative Vorticity",
            units="s-1",
            category="Dynamics",
            level_type="Pressure Level",
            renderer="Raster",
            colormap="vorticity",
        ),
        CatalogEntry(
            parameter_id="d",
            standard_name="divergence_of_wind",
            long_name="Horizontal Divergence",
            units="s-1",
            category="Dynamics",
            level_type="Pressure Level",
            renderer="Raster",
            colormap="divergence",
        ),
        CatalogEntry(
            parameter_id="clwc",
            standard_name="cloud_liquid_water_content",
            long_name="Cloud Liquid Water",
            units="kg kg-1",
            category="Cloud",
            level_type="Model Level",
            renderer="Raster",
            colormap="cloud_water",
        ),
        CatalogEntry(
            parameter_id="ciwc",
            standard_name="cloud_ice_water_content",
            long_name="Cloud Ice Water",
            units="kg kg-1",
            category="Cloud",
            level_type="Model Level",
            renderer="Raster",
            colormap="ice",
        ),
        CatalogEntry(
            parameter_id="crwc",
            standard_name="rain_water_content",
            long_name="Rain Water Mixing Ratio",
            units="kg kg-1",
            category="Hydrometeor",
            level_type="Model Level",
            renderer="Raster",
            colormap="rain",
        ),
        CatalogEntry(
            parameter_id="cswc",
            standard_name="snow_water_content",
            long_name="Snow Water Mixing Ratio",
            units="kg kg-1",
            category="Hydrometeor",
            level_type="Model Level",
            renderer="Raster",
            colormap="snow",
        ),
        CatalogEntry(
            parameter_id="graupel",
            standard_name="graupel_mixing_ratio",
            long_name="Graupel",
            units="kg kg-1",
            category="Hydrometeor",
            level_type="Model Level",
            renderer="Raster",
            colormap="graupel",
        ),
    ]

    for p in parameters:
        catalog.register(p)
