"""
Tests for acf.awci.config_loader - real external, versioned AWCI
configuration (docs/ACF_MASTER_PROMPT.md section 56: "Les seuils et
poids ne doivent pas être codés en dur partout. Prévoir une
configuration versionnée"). This session's exhaustive 90-section
conformance audit (reports/ACF_MASTER_AUDIT_v2.md) found the real,
already-configurable AWCICalculator (sections 22/45-47) had no
external file-based config loader.
"""

from __future__ import annotations

import json

import pytest

from acf.awci.calculator import AWCICalculator
from acf.awci.config_loader import load_config, save_default_config
from acf.awci.weights import WeightsManager

_DATA = {"temperature": 300.0, "wind_speed": 20.0, "cape": 1500.0, "altitude": 500.0}


def test_save_default_config_then_load_round_trips_to_a_bit_identical_calculator(tmp_path):
    path = tmp_path / "config.json"
    save_default_config(path, config_version="test-1")

    config = load_config(path)
    calc = config.build_calculator()
    default_calc = AWCICalculator()

    assert calc.calculate(dict(_DATA)) == default_calc.calculate(dict(_DATA))


def test_load_config_reads_the_real_config_version(tmp_path):
    path = tmp_path / "config.json"
    save_default_config(path, config_version="2026.09-v1")
    config = load_config(path)
    assert config.config_version == "2026.09-v1"


def test_save_default_config_matches_the_real_compiled_in_defaults(tmp_path):
    path = tmp_path / "config.json"
    save_default_config(path)
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["weights"] == WeightsManager.DEFAULT_WEIGHTS
    assert payload["interaction_weights"] == AWCICalculator.INTERACTION_WEIGHTS


def test_load_config_rejects_missing_required_keys(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"config_version": "x", "weights": {}}), encoding="utf-8")

    with pytest.raises(ValueError, match="missing required key"):
        load_config(path)


def test_load_config_propagates_invalid_interaction_configuration(tmp_path):
    """load_config() reuses AWCICalculator.__init__()'s own real
    validation - never reimplements it."""
    path = tmp_path / "config.json"
    payload = {
        "config_version": "x",
        "weights": dict(WeightsManager.DEFAULT_WEIGHTS),
        "interaction_terms": {"a": ["dynamic", "topographic"]},
        "interaction_weights": {"b": 0.05},  # mismatched key
        "level_thresholds": [[20.0, "Very Low"], [None, "Extreme"]],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="same keys"):
        load_config(path)


def test_load_config_propagates_invalid_level_thresholds(tmp_path):
    path = tmp_path / "config.json"
    payload = {
        "config_version": "x",
        "weights": dict(WeightsManager.DEFAULT_WEIGHTS),
        "interaction_terms": {},
        "interaction_weights": {},
        "level_thresholds": [[50.0, "High"], [20.0, "Low"]],  # not ascending
    }
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="ascending"):
        load_config(path)


def test_load_config_null_bound_becomes_real_infinity(tmp_path):
    path = tmp_path / "config.json"
    payload = {
        "config_version": "x",
        "weights": dict(WeightsManager.DEFAULT_WEIGHTS),
        "interaction_terms": {},
        "interaction_weights": {},
        "level_thresholds": [[50.0, "Below"], [None, "Above"]],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")

    config = load_config(path)

    assert config.level_thresholds[-1][0] == float("inf")


def test_a_real_custom_config_produces_a_genuinely_different_score(tmp_path):
    path = tmp_path / "config.json"
    payload = {
        "config_version": "custom-1",
        "weights": {
            "dynamic": 0.60,
            "thermodynamic": 0.10,
            "convective": 0.10,
            "microphysical": 0.10,
            "topographic": 0.05,
            "temporal": 0.025,
            "confidence": 0.025,
        },
        "interaction_terms": {},
        "interaction_weights": {},
        "level_thresholds": [[50.0, "Low"], [None, "High"]],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")

    custom_calc = load_config(path).build_calculator()
    default_result = AWCICalculator().calculate(dict(_DATA))
    custom_result = custom_calc.calculate(dict(_DATA))

    assert custom_result["awci"] != default_result["awci"]
    assert custom_result["level"] in {"Low", "High"}
