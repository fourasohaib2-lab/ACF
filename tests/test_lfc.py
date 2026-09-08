import math

import pytest

from acf.science.lfc import LFC


def test_lfc_exists():
    h = LFC.calculate(
        1200.0,
        20.0,
        18.0,
    )

    assert h == 1200.0


def test_no_lfc():
    h = LFC.calculate(
        1200.0,
        18.0,
        20.0,
    )

    assert math.isnan(h)


def test_invalid_height():
    with pytest.raises(ValueError):
        LFC.calculate(
            -10.0,
            20.0,
            18.0,
        )
