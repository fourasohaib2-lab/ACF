import pytest

from acf.science.mixing_ratio import MixingRatio


def test_mixing_ratio():
    w = MixingRatio.calculate(0.00990)
    assert round(w, 5) == 0.01


def test_zero():
    assert MixingRatio.calculate(0.0) == 0.0


def test_invalid_negative():
    with pytest.raises(ValueError):
        MixingRatio.calculate(-0.1)


def test_invalid_one():
    with pytest.raises(ValueError):
        MixingRatio.calculate(1.0)
