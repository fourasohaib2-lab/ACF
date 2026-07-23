import pytest

from acf.science.bulk_wind_shear import BulkWindShear


def test_bulk_wind_shear():

    value = BulkWindShear.calculate(
        u_bottom=5,
        v_bottom=2,
        u_top=20,
        v_top=10,
    )

    assert value == pytest.approx(17.0, abs=0.1)


def test_zero():

    value = BulkWindShear.calculate(
        u_bottom=10,
        v_bottom=5,
        u_top=10,
        v_top=5,
    )

    assert value == 0.0


def test_category():

    assert BulkWindShear.category(5) == "Weak"
    assert BulkWindShear.category(15) == "Moderate"
    assert BulkWindShear.category(25) == "Strong"
    assert BulkWindShear.category(40) == "Extreme"
