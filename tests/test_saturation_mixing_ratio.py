import pytest

from acf.science.saturation_mixing_ratio import SaturationMixingRatio


def test_saturation_mixing_ratio():
    # At 20°C, es ≈ 23.4 hPa, p = 1000 hPa
    ws = SaturationMixingRatio.calculate(23.4, 1000.0)
    # Expected: 0.622 * 23.4 / (1000 - 23.4) ≈ 0.0149
    assert round(ws, 4) == 0.0149


def test_invalid_pressure():
    with pytest.raises(ValueError):
        SaturationMixingRatio.calculate(100.0, 50.0)
