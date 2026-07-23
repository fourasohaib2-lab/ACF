from acf.science.saturation_mixing_ratio import SaturationMixingRatio

import pytest


def test_saturation_mixing_ratio():
    ws = SaturationMixingRatio.calculate(
        saturation_vapor_pressure=20.0,
        pressure=1000.0,
    )

    assert round(ws, 5) == 0.01269


def test_invalid_pressure():
    with pytest.raises(ValueError):
        SaturationMixingRatio.calculate(
            saturation_vapor_pressure=1000.0,
            pressure=1000.0,
        )
