from acf.science.mixing_ratio import MixingRatio

import pytest


def test_mixing_ratio():
    w = MixingRatio.calculate(
        vapor_pressure=20.0,
        pressure=1000.0,
    )

    assert round(w, 5) == 0.01269


def test_invalid_pressure():
    with pytest.raises(ValueError):
        MixingRatio.calculate(
            vapor_pressure=1000.0,
            pressure=1000.0,
        )
