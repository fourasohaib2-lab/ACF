"""
Tests for AWCI Calculator
=========================

Test AWCI calculation and decomposition.
"""

import pytest

from acf.awci.calculator import AWCICalculator
from acf.awci.normalizer import Normalizer
from acf.awci.weights import WeightsManager


def test_calculator_initialization():
    """Test calculator initialization."""
    calc = AWCICalculator()
    assert calc.weights_manager is not None
    assert calc.normalizer is not None


def test_calculate_module_scores():
    """Test module score calculation."""
    calc = AWCICalculator()
    data = {
        "temperature": 300.0,
        "specific_humidity": 0.01,
        "wind_speed": 10.0,
        "cape": 1000.0,
        "cin": -100.0,
        "precipitation": 5.0,
        "pressure": 1000.0,
        "altitude": 500.0,
        "confidence": 80.0,
        "temporal_change": 5.0,
    }

    scores = calc.calculate_module_scores(data)

    assert "dynamic" in scores
    assert "thermodynamic" in scores
    assert "convective" in scores
    assert "microphysical" in scores
    assert "topographic" in scores
    assert "temporal" in scores
    assert "confidence" in scores

    for score in scores.values():
        assert 0.0 <= score <= 1.0


def test_calculate_awci():
    """Test full AWCI calculation."""
    calc = AWCICalculator()
    data = {
        "temperature": 300.0,
        "specific_humidity": 0.01,
        "wind_speed": 10.0,
        "cape": 1000.0,
        "cin": -100.0,
        "precipitation": 5.0,
        "pressure": 1000.0,
        "altitude": 500.0,
        "confidence": 80.0,
        "temporal_change": 5.0,
    }

    result = calc.calculate(data)

    assert "awci" in result
    assert "decomposition" in result
    assert "level" in result
    assert "confidence" in result
    assert 0 <= result["awci"] <= 100
    assert result["level"] in ["Very Low", "Low", "Moderate", "High", "Very High", "Extreme"]


def test_decomposition_weights():
    """Test that decomposition sums to AWCI score (with rounding tolerance)."""
    calc = AWCICalculator()
    data = {
        "temperature": 300.0,
        "specific_humidity": 0.01,
        "wind_speed": 10.0,
        "cape": 1000.0,
        "cin": -100.0,
        "precipitation": 5.0,
        "pressure": 1000.0,
        "altitude": 500.0,
        "confidence": 80.0,
        "temporal_change": 5.0,
    }

    result = calc.calculate(data)
    decomposition = result["decomposition"]
    awci = result["awci"]

    # Sum of decomposition should equal AWCI (with rounding tolerance)
    total = sum(decomposition.values())
    # Augmenter la tolérance à 0.5 pour les arrondis
    assert total == pytest.approx(awci, abs=0.5)


def test_custom_weights():
    """Test custom weights in calculator."""
    custom_weights = {
        "dynamic": 0.30,
        "thermodynamic": 0.25,
        "convective": 0.20,
        "microphysical": 0.10,
        "topographic": 0.10,
        "temporal": 0.03,
        "confidence": 0.02,
    }

    calc = AWCICalculator(custom_weights)
    assert calc.weights_manager.get_weight("dynamic") == 0.30
    # Vérifier que la somme est toujours 1.0
    total = sum(calc.weights_manager.get_all_weights().values())
    assert total == pytest.approx(1.0, abs=0.01)


def test_empty_data():
    """Test calculator with empty data."""
    calc = AWCICalculator()
    data = {}

    # Should not raise errors, use defaults
    result = calc.calculate(data)
    assert result["awci"] >= 0
    assert result["level"] is not None


def test_calculate_includes_interaction_terms_and_stays_bounded():
    calc = AWCICalculator()
    # Push wind, topography, convection and thermodynamic modules all
    # high at once to stress-test the interaction terms' contribution.
    data = {
        "temperature": 320.0,
        "specific_humidity": 0.03,
        "wind_speed": 50.0,
        "cape": 5000.0,
        "cin": 0.0,
        "precipitation": 50.0,
        "pressure": 1000.0,
        "altitude": 3000.0,
        "confidence": 30.0,
        "temporal_change": 20.0,
    }

    result = calc.calculate(data)

    assert "interaction_scores" in result
    assert "wind_topo_interaction" in result["interaction_scores"]
    assert "conv_thermo_interaction" in result["interaction_scores"]
    assert 0.0 <= result["awci"] <= 100.0
    # decomposition (module + interaction terms) still sums to awci
    total = sum(result["decomposition"].values())
    assert total == pytest.approx(result["awci"], abs=0.5)


def test_calculate_interaction_scores_directly():
    calc = AWCICalculator()
    module_scores = {
        "dynamic": 0.8,
        "thermodynamic": 0.5,
        "convective": 0.9,
        "microphysical": 0.2,
        "topographic": 0.6,
        "temporal": 0.1,
        "confidence": 0.3,
    }
    interactions = calc.calculate_interaction_scores(module_scores)
    assert interactions["wind_topo_interaction"] == pytest.approx(0.8 * 0.6)
    assert interactions["conv_thermo_interaction"] == pytest.approx(0.9 * 0.5)


def test_explanation_present_and_ordered_by_contribution():
    calc = AWCICalculator()
    data = {
        "temperature": 300.0,
        "specific_humidity": 0.01,
        "wind_speed": 10.0,
        "cape": 1000.0,
        "cin": -100.0,
        "precipitation": 5.0,
        "pressure": 1000.0,
        "altitude": 500.0,
        "confidence": 80.0,
        "temporal_change": 5.0,
    }
    result = calc.calculate(data)
    explanation = result["explanation"]
    assert isinstance(explanation, list)
    assert len(explanation) > 0
    # Each line should carry the points value that appears in decomposition.
    for line in explanation:
        assert "points sur 100" in line


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


def test_normalizer_percentile_empty_climatology_is_neutral():
    norm = Normalizer()
    assert norm.normalize_percentile(25.0, []) == 0.5


def test_normalizer_percentile_known_ranking():
    norm = Normalizer()
    climatology = [10.0, 20.0, 30.0, 40.0, 50.0]
    assert norm.normalize_percentile(50.0, climatology) == pytest.approx(1.0)
    assert norm.normalize_percentile(10.0, climatology) == pytest.approx(0.2)
    assert norm.normalize_percentile(5.0, climatology) == pytest.approx(0.0)
    assert norm.normalize_percentile(30.0, climatology) == pytest.approx(0.6)


def test_weights_manager():
    """Test weights manager functionality."""
    # Créer un gestionnaire avec des poids personnalisés
    custom_weights = {
        "dynamic": 0.30,
        "thermodynamic": 0.20,
        "convective": 0.20,
        "microphysical": 0.10,
        "topographic": 0.10,
        "temporal": 0.05,
        "confidence": 0.05,
    }
    wm = WeightsManager(custom_weights)

    # Vérifier que les poids sont corrects
    assert wm.get_weight("dynamic") == 0.30
    assert wm.get_weight("confidence") == 0.05
    assert wm.get_weight("unknown") == 0.0

    # Utiliser update_weights pour modifier plusieurs poids en une fois
    wm.update_weights(
        {
            "dynamic": 0.25,
            "confidence": 0.10,
        }
    )
    assert wm.get_weight("dynamic") == 0.25
    assert wm.get_weight("confidence") == 0.10

    # CORRECTED: set_weight() used to change only the requested weight
    # and then validate that ALL weights summed to 1.0, which failed
    # for virtually any real single-weight change (the other weights
    # were untouched, so the sum drifted away from 1.0). It now
    # proportionally rescales the other weights instead. See weights.py.
    wm.reset()
    wm.set_weight("dynamic", 0.30)
    assert wm.get_weight("dynamic") == pytest.approx(0.30)
    assert sum(wm.get_all_weights().values()) == pytest.approx(1.0)

    # Reset to default
    wm.reset()
    assert wm.get_weight("dynamic") == 0.20
    assert wm.get_weight("confidence") == 0.05

    # Vérifier que la somme est toujours 1.0
    total = sum(wm.get_all_weights().values())
    assert total == pytest.approx(1.0, abs=0.01)
