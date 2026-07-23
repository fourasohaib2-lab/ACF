#!/usr/bin/env bash

set -e

PROJECT="/home/souhaib/ACF"

echo "============================================"
echo " Sprint 10 - Partie 4"
echo " Ocean & Wave Parameter Catalog"
echo "============================================"

##################################################
# OCEAN PARAMETERS
##################################################

cat > "$PROJECT/src/acf/catalog/ocean_parameters.py" << 'EOF'
from acf.catalog.catalog_entry import CatalogEntry


def register_ocean(catalog):

    parameters = [

        ####################################################
        # SEA SURFACE
        ####################################################

        CatalogEntry(
            parameter_id="sst",
            standard_name="sea_surface_temperature",
            long_name="Sea Surface Temperature",
            units="K",
            category="Ocean",
            level_type="Surface",
            renderer="Raster",
            colormap="sst"
        ),

        CatalogEntry(
            parameter_id="sss",
            standard_name="sea_surface_salinity",
            long_name="Sea Surface Salinity",
            units="psu",
            category="Ocean",
            level_type="Surface",
            renderer="Raster",
            colormap="salinity"
        ),

        ####################################################
        # OCEAN CURRENT
        ####################################################

        CatalogEntry(
            parameter_id="uo",
            standard_name="eastward_sea_water_velocity",
            long_name="Ocean Current U",
            units="m s-1",
            category="Ocean Current",
            level_type="Surface",
            renderer="Vector",
            colormap="current"
        ),

        CatalogEntry(
            parameter_id="vocean",
            standard_name="northward_sea_water_velocity",
            long_name="Ocean Current V",
            units="m s-1",
            category="Ocean Current",
            level_type="Surface",
            renderer="Vector",
            colormap="current"
        ),

        ####################################################
        # WAVES
        ####################################################

        CatalogEntry(
            parameter_id="swh",
            standard_name="significant_wave_height",
            long_name="Significant Wave Height",
            units="m",
            category="Wave",
            level_type="Surface",
            renderer="Raster",
            colormap="wave"
        ),

        CatalogEntry(
            parameter_id="mwd",
            standard_name="mean_wave_direction",
            long_name="Mean Wave Direction",
            units="degree",
            category="Wave",
            level_type="Surface",
            renderer="Vector",
            colormap="wave"
        ),

        CatalogEntry(
            parameter_id="mwp",
            standard_name="mean_wave_period",
            long_name="Mean Wave Period",
            units="s",
            category="Wave",
            level_type="Surface",
            renderer="Raster",
            colormap="wave"
        ),

        ####################################################
        # SEA ICE
        ####################################################

        CatalogEntry(
            parameter_id="sic",
            standard_name="sea_ice_area_fraction",
            long_name="Sea Ice Concentration",
            units="%",
            category="Sea Ice",
            level_type="Surface",
            renderer="Raster",
            colormap="ice"
        ),

        CatalogEntry(
            parameter_id="sit",
            standard_name="sea_ice_thickness",
            long_name="Sea Ice Thickness",
            units="m",
            category="Sea Ice",
            level_type="Surface",
            renderer="Raster",
            colormap="ice"
        )

    ]

    for parameter in parameters:
        catalog.register(parameter)

EOF

##################################################
# UPDATE DEFAULT CATALOG
##################################################

cat > "$PROJECT/src/acf/catalog/default_catalog.py" << 'EOF'
from acf.catalog.catalog import ScientificCatalog

from acf.catalog.surface_parameters import register_surface
from acf.catalog.atmospheric_parameters import register_atmosphere
from acf.catalog.ocean_parameters import register_ocean


def create_catalog():

    catalog = ScientificCatalog()

    register_surface(catalog)

    register_atmosphere(catalog)

    register_ocean(catalog)

    return catalog

EOF

##################################################
# TEST
##################################################

cat > "$PROJECT/tests/test_ocean_catalog.py" << 'EOF'
from acf.catalog.default_catalog import create_catalog


def test_ocean_catalog():

    catalog = create_catalog()

    assert catalog.exists("sst")
    assert catalog.exists("sss")
    assert catalog.exists("uo")
    assert catalog.exists("vocean")
    assert catalog.exists("swh")
    assert catalog.exists("mwd")
    assert catalog.exists("mwp")
    assert catalog.exists("sic")
    assert catalog.exists("sit")

    assert len(catalog.all()) >= 39

EOF

echo
echo "Ocean catalog installed successfully."
