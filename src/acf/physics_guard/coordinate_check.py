"""
Real latitude/longitude validation.

Directly motivated by a real bug this project found and fixed this
session: 'lons, lats = result["lats"], result["lons"]' (swapped) in
gui/dashboard/awci_dashboard.py, caught by a test using a deliberately
non-square grid where matplotlib immediately crashed
('Length of x (8) must match number of columns in z (14)'). A square
test grid - or a live call with real, plausible-looking swapped values -
would NOT have crashed, and a Physics Guard coordinate check on the
(lat, lon) pair would have caught it immediately regardless of grid
shape. That's the actual motivation for this module, not a generic
"nice to have".
"""

from acf.core.exceptions import CoordinateError


def check_coordinates(lat: float, lon: float) -> None:
    """
    Verify (lat, lon) are within real, physically valid Earth coordinate
    ranges.

    Parameters
    ----------
    lat : float
        Degrees, must be in [-90, 90].
    lon : float
        Degrees, must be in [-180, 180]. (ACF's real grids -
        acf.simulation_engine.numerical_core.earth_grid.EarthGrid -
        use this convention, not [0, 360].)

    Raises
    ------
    CoordinateError
        If lat or lon is out of range - including the common real bug
        of a swapped (lat, lon) pair, since a genuine longitude value
        outside [-90, 90] passed as latitude is exactly what this
        catches.
    """
    if not (-90.0 <= lat <= 90.0):
        raise CoordinateError(f"Latitude {lat} is outside [-90, 90] - possibly a swapped (lat, lon) pair")
    if not (-180.0 <= lon <= 180.0):
        raise CoordinateError(f"Longitude {lon} is outside [-180, 180]")


def check_coordinate_arrays(lats: list[float], lons: list[float]) -> None:
    """
    Verify every value in `lats`/`lons` is individually valid (see
    check_coordinates()), and that neither array is empty.

    Raises
    ------
    CoordinateError
        If either array is empty, or any individual value is invalid.
    """
    if len(lats) == 0 or len(lons) == 0:
        raise CoordinateError("lats/lons arrays must not be empty")

    for lat in lats:
        if not (-90.0 <= lat <= 90.0):
            raise CoordinateError(f"Latitude {lat} in lats array is outside [-90, 90]")
    for lon in lons:
        if not (-180.0 <= lon <= 180.0):
            raise CoordinateError(f"Longitude {lon} in lons array is outside [-180, 180]")
