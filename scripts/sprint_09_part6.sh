#!/usr/bin/env bash

set -e

PROJECT="/home/souhaib/ACF"

echo "=========================================="
echo " ACF Sprint 09 - Partie 6"
echo " Parameter Registry"
echo "=========================================="

mkdir -p "$PROJECT/src/acf/core"

touch "$PROJECT/src/acf/core/__init__.py"

##################################################
# PARAMETER
##################################################

cat > "$PROJECT/src/acf/core/parameter.py" << 'EOF'
from dataclasses import dataclass, field


@dataclass(slots=True)
class Parameter:

    id: str

    name: str

    units: str

    category: str

    renderer: str

    colormap: str

    description: str = ""

    alert_levels: dict = field(default_factory=dict)
EOF

##################################################
# REGISTRY
##################################################

cat > "$PROJECT/src/acf/core/parameter_registry.py" << 'EOF'
from acf.core.parameter import Parameter


class ParameterRegistry:

    def __init__(self):

        self.parameters = {}

    ##############################################

    def register(self, parameter):

        self.parameters[parameter.id] = parameter

    ##############################################

    def get(self, parameter_id):

        return self.parameters.get(parameter_id)

    ##############################################

    def exists(self, parameter_id):

        return parameter_id in self.parameters

    ##############################################

    def all(self):

        return list(self.parameters.values())

    ##############################################

    def categories(self):

        return sorted(
            {
                p.category
                for p in self.parameters.values()
            }
        )

    ##############################################

    def by_category(self, category):

        return [

            p

            for p in self.parameters.values()

            if p.category == category

        ]
EOF

##################################################
# DEFAULT PARAMETERS
##################################################

cat > "$PROJECT/src/acf/core/default_parameters.py" << 'EOF'
from acf.core.parameter import Parameter
from acf.core.parameter_registry import ParameterRegistry


def create_registry():

    registry = ParameterRegistry()

    registry.register(
        Parameter(
            id="t2m",
            name="2 m Temperature",
            units="°C",
            category="Surface",
            renderer="Raster",
            colormap="temperature",
            description="Air temperature at 2 metres"
        )
    )

    registry.register(
        Parameter(
            id="rh",
            name="Relative Humidity",
            units="%",
            category="Surface",
            renderer="Raster",
            colormap="humidity"
        )
    )

    registry.register(
        Parameter(
            id="mslp",
            name="Mean Sea Level Pressure",
            units="hPa",
            category="Surface",
            renderer="Contour",
            colormap="pressure"
        )
    )

    registry.register(
        Parameter(
            id="u10",
            name="10 m U Wind",
            units="m/s",
            category="Wind",
            renderer="Wind",
            colormap="wind"
        )
    )

    registry.register(
        Parameter(
            id="v10",
            name="10 m V Wind",
            units="m/s",
            category="Wind",
            renderer="Wind",
            colormap="wind"
        )
    )

    return registry
EOF

##################################################
# TESTS
##################################################

cat > "$PROJECT/tests/test_parameter_registry.py" << 'EOF'
from acf.core.default_parameters import create_registry


def test_registry():

    registry = create_registry()

    assert registry.exists("t2m")


def test_parameter():

    registry = create_registry()

    t = registry.get("t2m")

    assert t.units == "°C"

    assert t.renderer == "Raster"


def test_categories():

    registry = create_registry()

    assert "Surface" in registry.categories()
EOF

##################################################
# DEMO
##################################################

mkdir -p "$PROJECT/examples"

cat > "$PROJECT/examples/demo_parameter_registry.py" << 'EOF'
from acf.core.default_parameters import create_registry

registry = create_registry()

print()

print("Registered Parameters")

print("----------------------")

for parameter in registry.all():

    print(

        parameter.id,

        parameter.name,

        parameter.units,

        parameter.renderer

    )
EOF

echo
echo "Parameter Registry installed."
