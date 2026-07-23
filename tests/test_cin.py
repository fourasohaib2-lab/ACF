import pytest

from acf.science.cin import CIN


def test_positive_cin():

    cin = CIN.calculate(
        [18, 15, 10],
        [20, 17, 12],
        [0, 1000, 2000],
    )

    assert cin > 0


def test_zero_cin():

    cin = CIN.calculate(
        [20, 18, 15],
        [20, 18, 15],
        [0, 1000, 2000],
    )

    assert cin == 0


def test_invalid():

    with pytest.raises(ValueError):

        CIN.calculate(
            [20],
            [20, 18],
            [0],
        )
