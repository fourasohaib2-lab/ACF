"""
Tests for acf.fire_weather - the ACF Fire Weather Index (docs/
ACF_ARCHITECTURE_TARGET_GAP_MAP.md's layer 20, explicit user request
"vas-y, construis fire_weather/").

Real invariant-based testing throughout (documented ACF design choice,
not a reproduction of a published index's exact coefficients - see
fire_weather/__init__.py's own disclosure) rather than asserting exact
reference values that cannot be independently verified in this
environment.
"""

import pytest

from acf.fire_weather.calculator import FireWeatherCalculator
from acf.fire_weather.normalizer import FireWeatherNormalizer


def test_calculate_requires_core_inputs():
    calc = FireWeatherCalculator()
    with pytest.raises(KeyError, match="temperature"):
        calc.calculate({"relative_humidity": 50.0, "wind_speed": 5.0})


def test_calculate_returns_expected_structure():
    calc = FireWeatherCalculator()
    result = calc.calculate({"temperature": 25.0, "relative_humidity": 40.0, "wind_speed": 8.0})

    assert 0.0 <= result["fire_weather_index"] <= 100.0
    assert result["level"] in ["LOW", "MODERATE", "HIGH", "VERY_HIGH", "EXTREME"]
    assert set(result["decomposition"]) == {"humidity_dryness", "wind", "temperature", "fuel_dryness"}
    assert set(result["component_scores"]) == {"humidity_dryness", "wind", "temperature", "fuel_dryness"}


def test_decomposition_sums_to_index():
    calc = FireWeatherCalculator()
    result = calc.calculate({"temperature": 32.0, "relative_humidity": 15.0, "wind_speed": 12.0})
    assert sum(result["decomposition"].values()) == pytest.approx(result["fire_weather_index"], abs=0.2)


def test_lower_humidity_increases_index_real_physical_invariant():
    """Real physics: drier air -> drier fuel -> higher fire danger, all else equal."""
    calc = FireWeatherCalculator()
    base = {"temperature": 25.0, "wind_speed": 5.0}
    humid = calc.calculate({**base, "relative_humidity": 80.0})
    dry = calc.calculate({**base, "relative_humidity": 10.0})
    assert dry["fire_weather_index"] > humid["fire_weather_index"]


def test_higher_wind_increases_index_real_physical_invariant():
    calc = FireWeatherCalculator()
    base = {"temperature": 25.0, "relative_humidity": 40.0}
    calm = calc.calculate({**base, "wind_speed": 0.0})
    windy = calc.calculate({**base, "wind_speed": 18.0})
    assert windy["fire_weather_index"] > calm["fire_weather_index"]


def test_higher_temperature_increases_index_real_physical_invariant():
    calc = FireWeatherCalculator()
    base = {"relative_humidity": 40.0, "wind_speed": 5.0}
    cool = calc.calculate({**base, "temperature": 5.0})
    hot = calc.calculate({**base, "temperature": 40.0})
    assert hot["fire_weather_index"] > cool["fire_weather_index"]


def test_more_days_since_precipitation_increases_index():
    calc = FireWeatherCalculator()
    base = {"temperature": 25.0, "relative_humidity": 40.0, "wind_speed": 5.0}
    just_rained = calc.calculate({**base, "days_since_precipitation": 0.0})
    prolonged_dry = calc.calculate({**base, "days_since_precipitation": 21.0})
    assert prolonged_dry["fire_weather_index"] > just_rained["fire_weather_index"]


def test_days_since_precipitation_defaults_honestly_to_zero_not_fabricated():
    calc = FireWeatherCalculator()
    data = {"temperature": 25.0, "relative_humidity": 40.0, "wind_speed": 5.0}
    with_default = calc.calculate(data)
    explicit_zero = calc.calculate({**data, "days_since_precipitation": 0.0})
    assert with_default["fire_weather_index"] == pytest.approx(explicit_zero["fire_weather_index"])


def test_extreme_conditions_reach_extreme_level():
    calc = FireWeatherCalculator()
    result = calc.calculate(
        {"temperature": 42.0, "relative_humidity": 5.0, "wind_speed": 19.0, "days_since_precipitation": 21.0}
    )
    assert result["level"] == "EXTREME"
    assert result["fire_weather_index"] > 80.0


def test_calm_wet_conditions_reach_low_level():
    calc = FireWeatherCalculator()
    result = calc.calculate(
        {"temperature": 10.0, "relative_humidity": 95.0, "wind_speed": 1.0, "days_since_precipitation": 0.0}
    )
    assert result["level"] == "LOW"
    assert result["fire_weather_index"] < 20.0


def test_explanation_present_and_ordered_by_contribution():
    calc = FireWeatherCalculator()
    result = calc.calculate({"temperature": 30.0, "relative_humidity": 20.0, "wind_speed": 10.0})
    assert isinstance(result["explanation"], list)
    assert len(result["explanation"]) > 0
    for line in result["explanation"]:
        assert "points sur 100" in line


def test_custom_weights_must_sum_to_one():
    with pytest.raises(ValueError, match="sum to 1.0"):
        FireWeatherCalculator({"humidity_dryness": 0.5, "wind": 0.5, "temperature": 0.5, "fuel_dryness": 0.5})


def test_custom_weights_accepted_when_valid():
    calc = FireWeatherCalculator({"humidity_dryness": 0.4, "wind": 0.3, "temperature": 0.2, "fuel_dryness": 0.1})
    result = calc.calculate({"temperature": 25.0, "relative_humidity": 40.0, "wind_speed": 5.0})
    assert 0.0 <= result["fire_weather_index"] <= 100.0


def test_normalizer_methods_bounded_and_monotonic():
    norm = FireWeatherNormalizer()
    assert norm.normalize_temperature(0.0) == 0.0
    assert norm.normalize_temperature(45.0) == 1.0
    assert norm.normalize_temperature(100.0) == 1.0  # clamped, not extrapolated past 1.0

    assert norm.normalize_dryness_from_humidity(100.0) == 0.0
    assert norm.normalize_dryness_from_humidity(0.0) == 1.0

    assert norm.normalize_wind(0.0) == 0.0
    assert norm.normalize_wind(20.0) == 1.0
    assert norm.normalize_wind(50.0) == 1.0  # clamped

    assert norm.normalize_days_since_precipitation(0.0) == 0.0
    assert norm.normalize_days_since_precipitation(21.0) == 1.0
