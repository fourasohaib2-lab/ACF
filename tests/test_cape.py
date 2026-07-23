import pytest

from acf.science.cape import CAPE


def test_positive_cape():

    cape = CAPE.calculate(
        [22, 18, 14],
        [20, 16, 13],
        [0, 1000, 2000],
    )

    assert cape > 0


def test_zero_cape():

    cape = CAPE.calculate(
        [20, 18, 15],
        [20, 18, 15],
        [0, 1000, 2000],
    )

    assert cape == 0


def test_invalid():

    with pytest.raises(ValueError):
        CAPE.calculate(
            [20],
            [20, 18],
            [0],
        )
