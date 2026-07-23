#!/usr/bin/env bash

set -e

PROJECT="/home/souhaib/ACF"

echo "==========================================="
echo " ACF Sprint 10 - Partie 1"
echo " Scientific Parameter Catalog"
echo "==========================================="

mkdir -p "$PROJECT/src/acf/catalog"

touch "$PROJECT/src/acf/catalog/__init__.py"

##################################################
# PARAMETER ENTRY
##################################################

cat > "$PROJECT/src/acf/catalog/catalog_entry.py" << 'EOF'
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
EOF

##################################################
# CATALOG
##################################################

cat > "$PROJECT/src/acf/catalog/catalog.py" << 'EOF'
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
EOF

##################################################
# DEFAULT CATALOG
##################################################

cat > "$PROJECT/src/acf/catalog/default_catalog.py" << 'EOF'
from acf.catalog.catalog import ScientificCatalog
from acf.catalog.catalog_entry import CatalogEntry


def create_catalog():

    catalog = ScientificCatalog()

    catalog.register(
        CatalogEntry(
            parameter_id="t2m",
            standard_name="air_temperature",
            long_name="2 metre air temperature",
            units="K",
            category="Surface",
            level_type="2 m",
            renderer="Raster",
            colormap="temperature",
            cf_name="air_temperature",
            description="Air temperature measured at 2 metres."
        )
    )

    catalog.register(
        CatalogEntry(
            parameter_id="mslp",
            standard_name="air_pressure_at_mean_sea_level",
            long_name="Mean sea level pressure",
            units="Pa",
            category="Surface",
            level_type="Sea Level",
            renderer="Contour",
            colormap="pressure",
            cf_name="air_pressure_at_mean_sea_level",
            description="Pressure reduced to mean sea level."
        )
    )

    return catalog
EOF

##################################################
# TESTS
##################################################

cat > "$PROJECT/tests/test_scientific_catalog.py" << 'EOF'
from acf.catalog.default_catalog import create_catalog


def test_catalog_creation():

    catalog = create_catalog()

    assert catalog.exists("t2m")


def test_parameter_metadata():

    catalog = create_catalog()

    p = catalog.get("t2m")

    assert p.standard_name == "air_temperature"
    assert p.units == "K"
EOF

echo
echo "Scientific Catalog installed successfully."
