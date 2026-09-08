#!/usr/bin/env python3
"""
Test AWCI Display on MapCanvas
"""

import sys

import numpy as np
from PySide6.QtWidgets import QApplication

from acf.gui.map.map_canvas import MapCanvas


def generate_synthetic_awci_data():
    """Generate synthetic AWCI data for testing."""
    # Create grid
    lons = np.linspace(-10, 10, 60)
    lats = np.linspace(30, 50, 60)
    lon_grid, lat_grid = np.meshgrid(lons, lats)

    # Create a synthetic AWCI field with two centers of high complexity
    center1_lon, center1_lat = 3.0, 36.0  # Algeria
    center2_lon, center2_lat = 5.0, 40.0  # Mediterranean

    awci = (
        70 * np.exp(-((lon_grid - center1_lon) ** 2 + (lat_grid - center1_lat) ** 2) / 15)
        + 60 * np.exp(-((lon_grid - center2_lon) ** 2 + (lat_grid - center2_lat) ** 2) / 10)
        + np.random.normal(0, 3, lon_grid.shape)
    )
    awci = np.clip(awci, 0, 100)

    # Return dictionary with explicit keys
    return {"awci": awci, "longitude": lon_grid, "latitude": lat_grid}


def main():
    """Main test function."""
    app = QApplication(sys.argv)

    # Create canvas
    canvas = MapCanvas()
    canvas.render_base_map()

    # Generate data
    data = generate_synthetic_awci_data()

    # Vérification des données avant l'appel
    print(f"[Test] Type de data: {type(data)}")
    print(f"[Test] Clés disponibles: {list(data.keys())}")
    print(f"[Test] shape de awci: {data['awci'].shape}")
    print(f"[Test] shape de longitude: {data['longitude'].shape}")
    print(f"[Test] shape de latitude: {data['latitude'].shape}")

    # Render AWCI
    canvas.render_awci(data, colorbar=True, label="AWCI Complexity", levels=[0, 20, 35, 50, 65, 85, 100])

    # Show window
    canvas.show()
    canvas.setWindowTitle("AWCI Map - Test Display")

    print("✅ AWCI map displayed")
    print("Close the window to exit.")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
