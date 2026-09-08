"""
Atmospheric Complexity Framework (ACF)

CATALOG - Surface Parameters

Purpose:
--------
Provides parameter and dataset cataloging, indexing, and search capabilities.

Responsibilities:
-----------------
• Manage surface parameters logic and state representations.
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


def register_surface(catalog):

    parameters = [
        # Temperature
        CatalogEntry(
            parameter_id="t2m",
            standard_name="air_temperature",
            long_name="2 metre temperature",
            units="K",
            category="Surface",
            level_type="2 m",
            renderer="Raster",
            colormap="temperature",
        ),
        CatalogEntry(
            parameter_id="d2m",
            standard_name="dew_point_temperature",
            long_name="2 metre dew point",
            units="K",
            category="Surface",
            level_type="2 m",
            renderer="Raster",
            colormap="dewpoint",
        ),
        CatalogEntry(
            parameter_id="skin_temp",
            standard_name="surface_temperature",
            long_name="Surface skin temperature",
            units="K",
            category="Surface",
            level_type="Surface",
            renderer="Raster",
            colormap="temperature",
        ),
        # Humidity
        CatalogEntry(
            parameter_id="rh",
            standard_name="relative_humidity",
            long_name="Relative Humidity",
            units="%",
            category="Surface",
            level_type="2 m",
            renderer="Raster",
            colormap="humidity",
        ),
        CatalogEntry(
            parameter_id="q2",
            standard_name="specific_humidity",
            long_name="Specific Humidity",
            units="kg kg-1",
            category="Surface",
            level_type="2 m",
            renderer="Raster",
            colormap="humidity",
        ),
        # Wind
        CatalogEntry(
            parameter_id="u10",
            standard_name="eastward_wind",
            long_name="10 metre U Wind",
            units="m s-1",
            category="Wind",
            level_type="10 m",
            renderer="Wind",
            colormap="wind",
        ),
        CatalogEntry(
            parameter_id="v10",
            standard_name="northward_wind",
            long_name="10 metre V Wind",
            units="m s-1",
            category="Wind",
            level_type="10 m",
            renderer="Wind",
            colormap="wind",
        ),
        CatalogEntry(
            parameter_id="wind_speed",
            standard_name="wind_speed",
            long_name="Wind Speed",
            units="m s-1",
            category="Wind",
            level_type="10 m",
            renderer="Barbs",
            colormap="wind",
        ),
        CatalogEntry(
            parameter_id="wind_gust",
            standard_name="wind_speed_of_gust",
            long_name="Wind Gust",
            units="m s-1",
            category="Wind",
            level_type="10 m",
            renderer="Raster",
            colormap="wind",
        ),
        # Pressure
        CatalogEntry(
            parameter_id="mslp",
            standard_name="air_pressure_at_mean_sea_level",
            long_name="Mean Sea Level Pressure",
            units="Pa",
            category="Surface",
            level_type="MSL",
            renderer="Contour",
            colormap="pressure",
        ),
        # Rain
        CatalogEntry(
            parameter_id="tp",
            standard_name="precipitation_amount",
            long_name="Total precipitation",
            units="mm",
            category="Precipitation",
            level_type="Surface",
            renderer="Raster",
            colormap="rain",
        ),
        CatalogEntry(
            parameter_id="rain_conv",
            standard_name="convective_precipitation",
            long_name="Convective precipitation",
            units="mm",
            category="Precipitation",
            level_type="Surface",
            renderer="Raster",
            colormap="rain",
        ),
        CatalogEntry(
            parameter_id="snow",
            standard_name="snowfall_amount",
            long_name="Snowfall",
            units="mm",
            category="Precipitation",
            level_type="Surface",
            renderer="Raster",
            colormap="snow",
        ),
        # Clouds
        CatalogEntry(
            parameter_id="tcc",
            standard_name="cloud_area_fraction",
            long_name="Total Cloud Cover",
            units="%",
            category="Clouds",
            level_type="Atmosphere",
            renderer="Raster",
            colormap="clouds",
        ),
        # Radiation
        CatalogEntry(
            parameter_id="ssrd",
            standard_name="surface_downwelling_shortwave_flux",
            long_name="Solar Radiation",
            units="W m-2",
            category="Radiation",
            level_type="Surface",
            renderer="Raster",
            colormap="solar",
        ),
        # Soil
        CatalogEntry(
            parameter_id="soil_moisture",
            standard_name="soil_moisture_content",
            long_name="Soil Moisture",
            units="m3 m-3",
            category="Soil",
            level_type="Ground",
            renderer="Raster",
            colormap="soil",
        ),
    ]

    for p in parameters:
        catalog.register(p)
