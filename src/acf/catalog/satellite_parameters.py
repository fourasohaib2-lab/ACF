"""
Atmospheric Complexity Framework (ACF)

CATALOG - Satellite Parameters

Purpose:
--------
Provides parameter and dataset cataloging, indexing, and search capabilities.

Responsibilities:
-----------------
• Manage satellite parameters logic and state representations.
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


def register_satellite(catalog):

    parameters = [

        ####################################################
        # BRIGHTNESS TEMPERATURE
        ####################################################

        CatalogEntry(
            parameter_id="bt_ir108",
            standard_name="brightness_temperature",
            long_name="Brightness Temperature IR10.8",
            units="K",
            category="Satellite",
            level_type="TOA",
            renderer="Raster",
            colormap="infrared"
        ),

        CatalogEntry(
            parameter_id="bt_wv062",
            standard_name="brightness_temperature",
            long_name="Brightness Temperature WV6.2",
            units="K",
            category="Satellite",
            level_type="TOA",
            renderer="Raster",
            colormap="water_vapor"
        ),

        CatalogEntry(
            parameter_id="bt_vis006",
            standard_name="toa_bidirectional_reflectance",
            long_name="Visible Reflectance",
            units="%",
            category="Satellite",
            level_type="TOA",
            renderer="Raster",
            colormap="visible"
        ),

        ####################################################
        # CLOUD PRODUCTS
        ####################################################

        CatalogEntry(
            parameter_id="cth",
            standard_name="cloud_top_height",
            long_name="Cloud Top Height",
            units="m",
            category="Satellite",
            level_type="Atmosphere",
            renderer="Raster",
            colormap="cloud_height"
        ),

        CatalogEntry(
            parameter_id="ctt",
            standard_name="cloud_top_temperature",
            long_name="Cloud Top Temperature",
            units="K",
            category="Satellite",
            level_type="Atmosphere",
            renderer="Raster",
            colormap="temperature"
        ),

        CatalogEntry(
            parameter_id="cot",
            standard_name="cloud_optical_thickness",
            long_name="Cloud Optical Thickness",
            units="1",
            category="Satellite",
            level_type="Atmosphere",
            renderer="Raster",
            colormap="clouds"
        ),

        ####################################################
        # RADAR
        ####################################################

        CatalogEntry(
            parameter_id="dbz",
            standard_name="equivalent_reflectivity_factor",
            long_name="Radar Reflectivity",
            units="dBZ",
            category="Radar",
            level_type="Volume",
            renderer="Raster",
            colormap="reflectivity"
        ),

        CatalogEntry(
            parameter_id="vrad",
            standard_name="radial_velocity",
            long_name="Radial Velocity",
            units="m s-1",
            category="Radar",
            level_type="Volume",
            renderer="Raster",
            colormap="velocity"
        ),

        CatalogEntry(
            parameter_id="zdr",
            standard_name="differential_reflectivity",
            long_name="Differential Reflectivity",
            units="dB",
            category="Radar",
            level_type="Volume",
            renderer="Raster",
            colormap="zdr"
        ),

        CatalogEntry(
            parameter_id="kdp",
            standard_name="specific_differential_phase",
            long_name="Specific Differential Phase",
            units="deg km-1",
            category="Radar",
            level_type="Volume",
            renderer="Raster",
            colormap="kdp"
        ),

        CatalogEntry(
            parameter_id="rhohv",
            standard_name="cross_correlation_ratio",
            long_name="Cross Correlation Ratio",
            units="1",
            category="Radar",
            level_type="Volume",
            renderer="Raster",
            colormap="rhohv"
        )

    ]

    for p in parameters:
        catalog.register(p)
