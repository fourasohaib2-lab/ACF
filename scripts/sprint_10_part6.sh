#!/usr/bin/env bash

set -e

PROJECT="/home/souhaib/ACF"

echo "==============================================="
echo " Sprint 10 - Partie 6"
echo " Climate & Air Quality Catalog"
echo "==============================================="

##################################################
# CLIMATE & AIR QUALITY
##################################################

cat > "$PROJECT/src/acf/catalog/climate_parameters.py" << 'EOF'
from acf.catalog.catalog_entry import CatalogEntry


def register_climate(catalog):

    parameters = [

        ####################################################
        # CLIMATE INDICES
        ####################################################

        CatalogEntry(
            parameter_id="enso",
            standard_name="enso_index",
            long_name="El Niño Southern Oscillation",
            units="index",
            category="Climate",
            level_type="Global",
            renderer="TimeSeries",
            colormap="enso"
        ),

        CatalogEntry(
            parameter_id="nao",
            standard_name="north_atlantic_oscillation",
            long_name="North Atlantic Oscillation",
            units="index",
            category="Climate",
            level_type="Global",
            renderer="TimeSeries",
            colormap="nao"
        ),

        CatalogEntry(
            parameter_id="ao",
            standard_name="arctic_oscillation",
            long_name="Arctic Oscillation",
            units="index",
            category="Climate",
            level_type="Global",
            renderer="TimeSeries",
            colormap="ao"
        ),

        CatalogEntry(
            parameter_id="mjo",
            standard_name="madden_julian_oscillation",
            long_name="Madden-Julian Oscillation",
            units="index",
            category="Climate",
            level_type="Global",
            renderer="TimeSeries",
            colormap="mjo"
        ),

        ####################################################
        # AIR QUALITY
        ####################################################

        CatalogEntry(
            parameter_id="pm25",
            standard_name="pm2p5_mass_concentration",
            long_name="PM2.5",
            units="µg m-3",
            category="Air Quality",
            level_type="Surface",
            renderer="Raster",
            colormap="pollution"
        ),

        CatalogEntry(
            parameter_id="pm10",
            standard_name="pm10_mass_concentration",
            long_name="PM10",
            units="µg m-3",
            category="Air Quality",
            level_type="Surface",
            renderer="Raster",
            colormap="pollution"
        ),

        CatalogEntry(
            parameter_id="o3",
            standard_name="ozone_mass_concentration",
            long_name="Ozone",
            units="µg m-3",
            category="Air Quality",
            level_type="Surface",
            renderer="Raster",
            colormap="ozone"
        ),

        CatalogEntry(
            parameter_id="no2",
            standard_name="nitrogen_dioxide_mass_concentration",
            long_name="Nitrogen Dioxide",
            units="µg m-3",
            category="Air Quality",
            level_type="Surface",
            renderer="Raster",
            colormap="pollution"
        ),

        CatalogEntry(
            parameter_id="so2",
            standard_name="sulfur_dioxide_mass_concentration",
            long_name="Sulfur Dioxide",
            units="µg m-3",
            category="Air Quality",
            level_type="Surface",
            renderer="Raster",
            colormap="pollution"
        ),

        CatalogEntry(
            parameter_id="co",
            standard_name="carbon_monoxide_mass_concentration",
            long_name="Carbon Monoxide",
            units="mg m-3",
            category="Air Quality",
            level_type="Surface",
            renderer="Raster",
            colormap="pollution"
        ),

        ####################################################
        # GREENHOUSE GASES
        ####################################################

        CatalogEntry(
            parameter_id="co2",
            standard_name="carbon_dioxide_mole_fraction",
            long_name="Carbon Dioxide",
            units="ppm",
            category="Greenhouse Gas",
            level_type="Atmosphere",
            renderer="Raster",
            colormap="co2"
        ),

        CatalogEntry(
            parameter_id="ch4",
            standard_name="methane_mole_fraction",
            long_name="Methane",
            units="ppb",
            category="Greenhouse Gas",
            level_type="Atmosphere",
            renderer="Raster",
            colormap="methane"
        ),

        ####################################################
        # AEROSOLS
        ####################################################

        CatalogEntry(
            parameter_id="aod550",
            standard_name="atmosphere_optical_thickness_due_to_ambient_aerosol",
            long_name="Aerosol Optical Depth 550 nm",
            units="1",
            category="Aerosol",
            level_type="Column",
            renderer="Raster",
            colormap="dust"
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
from acf.catalog.climate_parameters import register_climate


def create_catalog():

    catalog = ScientificCatalog()

    register_surface(catalog)
    register_atmosphere(catalog)
    register_ocean(catalog)
    register_satellite(catalog)
    register_climate(catalog)

    return catalog
EOF

##################################################
# TESTS
##################################################

cat > "$PROJECT/tests/test_climate_catalog.py" << 'EOF'
from acf.catalog.default_catalog import create_catalog


def test_climate_catalog():

    catalog = create_catalog()

    assert catalog.exists("enso")
    assert catalog.exists("nao")
    assert catalog.exists("ao")
    assert catalog.exists("mjo")

    assert catalog.exists("pm25")
    assert catalog.exists("pm10")
    assert catalog.exists("o3")
    assert catalog.exists("no2")
    assert catalog.exists("so2")
    assert catalog.exists("co")

    assert catalog.exists("co2")
    assert catalog.exists("ch4")

    assert catalog.exists("aod550")

    assert len(catalog.all()) >= 63
EOF

echo
echo "Climate & Air Quality catalog installed successfully."
