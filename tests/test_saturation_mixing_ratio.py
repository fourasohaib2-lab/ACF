from acf.science.saturation_mixing_ratio import SaturationMixingRatio

def test_saturation_mixing_ratio():
    # At 20°C, es ≈ 23.4 hPa, p = 1000 hPa
    ws = SaturationMixingRatio.calculate(23.4, 1000.0)
    # Expected: 0.622 * 23.4 / (1000 - 23.4) ≈ 0.0149
    assert round(ws, 4) == 0.0149

def test_invalid_pressure():
    try:
        SaturationMixingRatio.calculate(100.0, 50.0)
        assert False, "Should raise ValueError"
    except ValueError:
        pass
