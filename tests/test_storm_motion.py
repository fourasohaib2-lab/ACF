import math

import pytest

from acf.science.storm_motion import StormMotion


def test_storm_motion():

    u, v = StormMotion.calculate(
        mean_u=10,
        mean_v=5,
    )

    assert u == pytest.approx(17.5)
    assert v == pytest.approx(12.5)


def test_bunkers_storm_motion_deviates_perpendicular_to_shear():
    """
    CORRECTED: StormMotion.calculate() only ever added a fixed
    (7.5, 7.5) m/s offset regardless of any shear direction, despite
    its docstring claiming "Approximate Bunkers storm motion" - real
    Bunkers (2000) motion deviates perpendicular to the actual 0-6 km
    shear vector. calculate_bunkers() now implements the real method.

    For eastward shear (wind speed increasing with height, blowing due
    east throughout), the Northern-Hemisphere right-mover must deviate
    to the right of the shear vector - facing east, "right" is south
    (negative v) - and the left-mover to the north (positive v), with
    both movers' u-component unchanged from the mean wind (since the
    deviation is purely perpendicular to a due-east shear vector).
    """
    result = StormMotion.calculate_bunkers(mean_u=10.0, mean_v=5.0, shear_u=20.0, shear_v=0.0)

    right_u, right_v = result["right_mover"]
    left_u, left_v = result["left_mover"]

    assert right_u == pytest.approx(10.0)
    assert right_v == pytest.approx(5.0 - 7.5)
    assert left_u == pytest.approx(10.0)
    assert left_v == pytest.approx(5.0 + 7.5)

    # Both movers deviate from the mean wind by exactly the Bunkers
    # empirical magnitude (7.5 m/s), never a different distance.
    assert math.hypot(right_u - 10.0, right_v - 5.0) == pytest.approx(7.5)
    assert math.hypot(left_u - 10.0, left_v - 5.0) == pytest.approx(7.5)


def test_bunkers_storm_motion_rejects_zero_shear():
    with pytest.raises(ValueError):
        StormMotion.calculate_bunkers(mean_u=10.0, mean_v=5.0, shear_u=0.0, shear_v=0.0)
