#!/usr/bin/env bash

set -e

PROJECT="/home/souhaib/ACF"

echo "======================================="
echo " ACF Sprint 07 - Part 3"
echo " Projection Engine"
echo "======================================="

####################################################
# Projection Manager
####################################################

cat > "$PROJECT/src/acf/maps/projections/projection_manager.py" << 'EOF'
"""
Projection Manager
"""

class ProjectionManager:
    """
    Gestionnaire des projections cartographiques.

    Les noms sont indépendants de Cartopy afin que
    l'application reste facilement extensible.
    """

    def __init__(self):

        self._projections = {
            "platecarree": "PlateCarree",
            "mercator": "Mercator",
            "lambert": "LambertConformal",
            "polar": "NorthPolarStereo",
            "south_polar": "SouthPolarStereo",
            "orthographic": "Orthographic",
            "robinson": "Robinson",
        }

        self._current = "platecarree"

    ##################################################

    def available(self):

        return sorted(self._projections.keys())

    ##################################################

    def current(self):

        return self._current

    ##################################################

    def set(self, name):

        if name not in self._projections:
            raise ValueError(
                f"Projection inconnue : {name}"
            )

        self._current = name

    ##################################################

    def cartopy_name(self):

        return self._projections[self._current]
EOF

####################################################
# Tests
####################################################

cat > "$PROJECT/tests/test_projection_manager.py" << 'EOF'
from acf.maps.projections.projection_manager import ProjectionManager

def test_default_projection():

    manager = ProjectionManager()

    assert manager.current() == "platecarree"


def test_change_projection():

    manager = ProjectionManager()

    manager.set("mercator")

    assert manager.current() == "mercator"


def test_cartopy_name():

    manager = ProjectionManager()

    manager.set("lambert")

    assert manager.cartopy_name() == "LambertConformal"


def test_available():

    manager = ProjectionManager()

    assert "mercator" in manager.available()
    assert "lambert" in manager.available()
EOF

echo
echo "Projection Engine installed successfully."

