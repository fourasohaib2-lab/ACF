from acf.science.saturation_vapor_pressure import SaturationVaporPressure

def test_tetens_0c():
    # At 0°C, es should be ≈ 6.112 hPa
    es = SaturationVaporPressure.calculate_tetens(273.15, is_kelvin=True)
    assert round(es, 3) == 6.112

def test_tetens_20c():
    # At 20°C, es should be ≈ 23.37 hPa
    es = SaturationVaporPressure.calculate_tetens(293.15, is_kelvin=True)
    assert round(es, 2) == 23.37

def test_tetens_celsius():
    # At 20°C directly
    es = SaturationVaporPressure.calculate_tetens(20.0, is_kelvin=False)
    assert round(es, 2) == 23.37
