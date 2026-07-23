#!/usr/bin/env bash

set -e

PROJECT="/home/souhaib/ACF"

echo "==============================================="
echo " Sprint 10 - Partie 7"
echo " Parameter Alias & Mapping Engine"
echo "==============================================="

mkdir -p "$PROJECT/src/acf/catalog"

##################################################
# PARAMETER MAPPING ENGINE
##################################################

cat > "$PROJECT/src/acf/catalog/parameter_mapper.py" << 'EOF'
class ParameterMapper:

    def __init__(self):

        self.aliases = {}

    ##################################################

    def register(self, canonical_name, *aliases):

        canonical = canonical_name.lower()

        self.aliases[canonical] = canonical

        for alias in aliases:
            self.aliases[alias.lower()] = canonical

    ##################################################

    def resolve(self, variable):

        if variable is None:
            return None

        return self.aliases.get(variable.lower())

    ##################################################

    def exists(self, variable):

        return self.resolve(variable) is not None

    ##################################################

    def all_aliases(self):

        return dict(self.aliases)
EOF

##################################################
# DEFAULT MAPPING
##################################################

cat > "$PROJECT/src/acf/catalog/default_mapping.py" << 'EOF'
from acf.catalog.parameter_mapper import ParameterMapper


def create_default_mapper():

    mapper = ParameterMapper()

    ########################################
    # Temperature
    ########################################

    mapper.register(
        "t2m",
        "T2",
        "TMP",
        "TMP_2m",
        "2T",
        "air_temperature",
        "t_2m"
    )

    ########################################
    # Dew Point
    ########################################

    mapper.register(
        "d2m",
        "TD2",
        "dewpoint",
        "dew_point_temperature"
    )

    ########################################
    # Pressure
    ########################################

    mapper.register(
        "mslp",
        "MSL",
        "PRMSL",
        "MeanSeaLevelPressure"
    )

    ########################################
    # Wind
    ########################################

    mapper.register(
        "u10",
        "U10",
        "UGRD",
        "u_wind_10m"
    )

    mapper.register(
        "v10",
        "V10",
        "VGRD",
        "v_wind_10m"
    )

    ########################################
    # Humidity
    ########################################

    mapper.register(
        "rh",
        "RH",
        "RelativeHumidity"
    )

    mapper.register(
        "q",
        "QVAPOR",
        "specific_humidity"
    )

    ########################################
    # Rain
    ########################################

    mapper.register(
        "tp",
        "RAIN",
        "RAINC",
        "RAINNC",
        "precipitation"
    )

    return mapper
EOF

##################################################
# TESTS
##################################################

cat > "$PROJECT/tests/test_parameter_mapper.py" << 'EOF'
from acf.catalog.default_mapping import create_default_mapper


def test_temperature_mapping():

    mapper = create_default_mapper()

    assert mapper.resolve("T2") == "t2m"
    assert mapper.resolve("TMP") == "t2m"
    assert mapper.resolve("2T") == "t2m"
    assert mapper.resolve("air_temperature") == "t2m"


def test_wrf_mapping():

    mapper = create_default_mapper()

    assert mapper.resolve("QVAPOR") == "q"
    assert mapper.resolve("RAINNC") == "tp"
    assert mapper.resolve("RAINC") == "tp"


def test_unknown():

    mapper = create_default_mapper()

    assert mapper.resolve("ABCXYZ") is None
EOF

echo
echo "Parameter Mapping Engine installed successfully."

