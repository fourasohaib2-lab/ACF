"""
Tests for AWCI Calculator
=========================

Test AWCI calculation and decomposition.
"""

import pytest
from acf.awci.calculator import AWCICalculator
from acf.awci.weights import WeightsManager
from acf.awci.normalizer import Normalizer


def test_calculator_initialization():
    """Test calculator initialization."""
    calc = AWCICalculator()
    assert calc.weights_manager is not None
    assert calc.normalizer is not None


def test_calculate_module_scores():
    """Test module score calculation."""
    calc = AWCICalculator()
    data = {
        'temperature': 300.0,
        'specific_humidity': 0.01,
        'wind_speed': 10.0,
        'cape': 1000.0,
        'cin': -100.0,
        'precipitation': 5.0,
        'pressure': 1000.0,
        'altitude': 500.0,
        'confidence': 80.0,
        'temporal_change': 5.0,
    }
    
    scores = calc.calculate_module_scores(data)
    
    assert 'dynamic' in scores
    assert 'thermodynamic' in scores
    assert 'convective' in scores
    assert 'microphysical' in scores
    assert 'topographic' in scores
    assert 'temporal' in scores
    assert 'confidence' in scores
    
    for score in scores.values():
        assert 0.0 <= score <= 1.0


def test_calculate_awci():
    """Test full AWCI calculation."""
    calc = AWCICalculator()
    data = {
        'temperature': 300.0,
        'specific_humidity': 0.01,
        'wind_speed': 10.0,
        'cape': 1000.0,
        'cin': -100.0,
        'precipitation': 5.0,
        'pressure': 1000.0,
        'altitude': 500.0,
        'confidence': 80.0,
        'temporal_change': 5.0,
    }
    
    result = calc.calculate(data)
    
    assert 'awci' in result
    assert 'decomposition' in result
    assert 'level' in result
    assert 'confidence' in result
    assert 0 <= result['awci'] <= 100
    assert result['level'] in ['Very Low', 'Low', 'Moderate', 'High', 'Very High', 'Extreme']


def test_decomposition_weights():
    """Test that decomposition sums to AWCI score (with rounding tolerance)."""
    calc = AWCICalculator()
    data = {
        'temperature': 300.0,
        'specific_humidity': 0.01,
        'wind_speed': 10.0,
        'cape': 1000.0,
        'cin': -100.0,
        'precipitation': 5.0,
        'pressure': 1000.0,
        'altitude': 500.0,
        'confidence': 80.0,
        'temporal_change': 5.0,
    }
    
    result = calc.calculate(data)
    decomposition = result['decomposition']
    awci = result['awci']
    
    # Sum of decomposition should equal AWCI (with rounding tolerance)
    total = sum(decomposition.values())
    # Augmenter la tolérance à 0.5 pour les arrondis
    assert total == pytest.approx(awci, abs=0.5)


def test_custom_weights():
    """Test custom weights in calculator."""
    custom_weights = {
        'dynamic': 0.30,
        'thermodynamic': 0.25,
        'convective': 0.20,
        'microphysical': 0.10,
        'topographic': 0.10,
        'temporal': 0.03,
        'confidence': 0.02,
    }
    
    calc = AWCICalculator(custom_weights)
    assert calc.weights_manager.get_weight('dynamic') == 0.30
    # Vérifier que la somme est toujours 1.0
    total = sum(calc.weights_manager.get_all_weights().values())
    assert total == pytest.approx(1.0, abs=0.01)


def test_empty_data():
    """Test calculator with empty data."""
    calc = AWCICalculator()
    data = {}
    
    # Should not raise errors, use defaults
    result = calc.calculate(data)
    assert result['awci'] >= 0
    assert result['level'] is not None


def test_normalizer_methods():
    """Test normalizer methods individually."""
    norm = Normalizer()
    
    assert 0.0 <= norm.normalize_temperature(300.0) <= 1.0
    assert 0.0 <= norm.normalize_wind(10.0) <= 1.0
    assert 0.0 <= norm.normalize_humidity(0.01) <= 1.0
    assert 0.0 <= norm.normalize_cape(1000.0) <= 1.0
    assert 0.0 <= norm.normalize_cin(-100.0) <= 1.0
    assert 0.0 <= norm.normalize_precipitation(5.0) <= 1.0
    assert 0.0 <= norm.normalize_confidence(80.0) <= 1.0


def test_weights_manager():
    """Test weights manager functionality."""
    # Créer un gestionnaire avec des poids personnalisés
    custom_weights = {
        'dynamic': 0.30,
        'thermodynamic': 0.20,
        'convective': 0.20,
        'microphysical': 0.10,
        'topographic': 0.10,
        'temporal': 0.05,
        'confidence': 0.05,
    }
    wm = WeightsManager(custom_weights)
    
    # Vérifier que les poids sont corrects
    assert wm.get_weight('dynamic') == 0.30
    assert wm.get_weight('confidence') == 0.05
    assert wm.get_weight('unknown') == 0.0
    
    # Utiliser update_weights pour modifier plusieurs poids en une fois
    wm.update_weights({
        'dynamic': 0.25,
        'confidence': 0.10,
    })
    assert wm.get_weight('dynamic') == 0.25
    assert wm.get_weight('confidence') == 0.10
    
    # Reset to default
    wm.reset()
    assert wm.get_weight('dynamic') == 0.20
    assert wm.get_weight('confidence') == 0.05
    
    # Vérifier que la somme est toujours 1.0
    total = sum(wm.get_all_weights().values())
    assert total == pytest.approx(1.0, abs=0.01)
