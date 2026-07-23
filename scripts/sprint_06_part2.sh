#!/usr/bin/env bash

set -e

PROJECT="/home/souhaib/ACF"

echo "========================================"
echo " ACF Sprint 06 - Part 2"
echo " Dataset Class"
echo "========================================"

cat > "$PROJECT/src/acf/data/dataset.py" << 'EOF'
"""
ACF Scientific Dataset
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class Dataset:
    """
    Représente un jeu de données scientifique.
    """

    name: str
    filepath: Path
    filetype: str

    variables: list = field(default_factory=list)
    dimensions: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)

    loaded_at: str = field(
        default_factory=lambda: datetime.now().isoformat()
    )

    def exists(self) -> bool:
        """Vérifie que le fichier existe."""
        return self.filepath.exists()

    def add_variable(self, variable: str):
        """Ajoute une variable."""
        if variable not in self.variables:
            self.variables.append(variable)

    def set_dimension(self, name: str, size: int):
        """Déclare une dimension."""
        self.dimensions[name] = size

    def set_metadata(self, key: str, value):
        """Ajoute une métadonnée."""
        self.metadata[key] = value

    def summary(self):
        """Retourne un résumé du Dataset."""
        return {
            "name": self.name,
            "file": str(self.filepath),
            "type": self.filetype,
            "variables": len(self.variables),
            "dimensions": self.dimensions,
            "metadata": len(self.metadata),
        }
EOF

mkdir -p "$PROJECT/tests"

cat > "$PROJECT/tests/test_dataset.py" << 'EOF'
from pathlib import Path

from acf.data.dataset import Dataset


def test_dataset_creation():

    ds = Dataset(
        name="WRF",
        filepath=Path("/tmp/test.nc"),
        filetype="NetCDF",
    )

    assert ds.name == "WRF"
    assert ds.filetype == "NetCDF"


def test_add_variable():

    ds = Dataset(
        name="Demo",
        filepath=Path("/tmp/test.nc"),
        filetype="NetCDF",
    )

    ds.add_variable("Temperature")
    ds.add_variable("Pressure")

    assert len(ds.variables) == 2


def test_dimension():

    ds = Dataset(
        name="Demo",
        filepath=Path("/tmp/test.nc"),
        filetype="NetCDF",
    )

    ds.set_dimension("time", 24)

    assert ds.dimensions["time"] == 24
EOF

echo
echo "Dataset class successfully created."
