#!/usr/bin/env bash

set -e

PROJECT="/home/souhaib/ACF"

echo "==============================================="
echo " Sprint 10 - Partie 5"
echo " Satellite & Radar Parameter Catalog"
echo "==============================================="

##################################################
# SATELLITE + RADAR
##################################################

cat > "$PROJECT/src/acf/catalog/satellite_parameters.py" << 'EOF'
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
EOF

##################################################
# UPDATE DEFAULT CATALOG
##################################################

cat > "$PROJECT/src/acf/catalog/default_catalog.py" << 'EOF'
from acf.catalog.catalog import ScientificCatalog
from acf.catalog.surface_parameters import register_surface
from acf.catalog.atmospheric_parameters import register_atmosphere
from acf.catalog.ocean_parameters import register_ocean
from acf.catalog.satellite_parameters import register_satellite


def create_catalog():

    catalog = ScientificCatalog()

    register_surface(catalog)
    register_atmosphere(catalog)
    register_ocean(catalog)
    register_satellite(catalog)

    return catalog
EOF

##################################################
# TEST
##################################################

cat > "$PROJECT/tests/test_satellite_catalog.py" << 'EOF'
from acf.catalog.default_catalog import create_catalog


def test_satellite_catalog():

    catalog = create_catalog()

    assert catalog.exists("bt_ir108")
    assert catalog.exists("cth")
    assert catalog.exists("dbz")
    assert catalog.exists("vrad")
    assert catalog.exists("zdr")
    assert catalog.exists("kdp")
    assert catalog.exists("rhohv")

    assert len(catalog.all()) >= 50
EOF

echo
echo "Satellite & Radar catalog installed successfully."
