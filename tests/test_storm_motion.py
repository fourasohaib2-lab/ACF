import pytest

from acf.science.storm_motion import StormMotion


def test_storm_motion():

    u, v = StormMotion.calculate(
        mean_u=10,
        mean_v=5,
    )

    assert u == pytest.approx(17.5)
    assert v == pytest.approx(12.5)
