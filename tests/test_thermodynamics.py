import pytest
from acf.science.thermodynamics import Thermodynamics

def test_virtual_temperature_formula():
    """Test virtual temperature calculation."""
    T = 300.0
    q = 0.01
    result = Thermodynamics.calculate_virtual_temperature(T, q)
    assert result == pytest.approx(301.83, abs=0.01)

def test_mixing_ratio_formula():
    """Test mixing ratio calculation."""
    q = 0.01
    result = Thermodynamics.calculate_mixing_ratio(q)
    assert result == pytest.approx(0.01010, abs=0.00001)

def test_saturation_vapor_pressure_formula():
    """Test saturation vapor pressure at 300K."""
    T = 300.0
    result = Thermodynamics.calculate_saturation_vapor_pressure(T)
    assert result == pytest.approx(35.35, abs=0.1)

def test_vapor_pressure_formula():
    """Test vapor pressure calculation."""
    q = 0.01
    p = 1000.0
    result = Thermodynamics.calculate_vapor_pressure(q, p)
    assert result == pytest.approx(15.98, abs=0.01)

def test_relative_humidity_formula():
    """Test relative humidity calculation."""
    q = 0.01
    p = 1000.0
    T = 300.0
    result = Thermodynamics.calculate_relative_humidity(q, p, T)
    assert result == pytest.approx(45.2, abs=0.1)

def test_all_formulas_no_errors():
    """Test that all formulas run without errors."""
    T = 280.0
    p = 900.0
    q = 0.005
    
    assert Thermodynamics.calculate_virtual_temperature(T, q) > 0
    assert Thermodynamics.calculate_mixing_ratio(q) > 0
    assert Thermodynamics.calculate_saturation_mixing_ratio(10.0, p) > 0
    assert Thermodynamics.calculate_vapor_pressure(q, p) > 0
    assert Thermodynamics.calculate_saturation_vapor_pressure(T) > 0
    assert Thermodynamics.calculate_relative_humidity(q, p, T) >= 0
