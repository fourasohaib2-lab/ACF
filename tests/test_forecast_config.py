"""
Unit test suite for ForecastConfig (ACF-NWP-001).
"""

from pathlib import Path

from acf.models.forecast_config import ForecastConfig


def test_forecast_config_defaults():
    """Test default values and validation."""
    cfg = ForecastConfig()
    assert cfg.model_name == "AROME"
    assert cfg.forecast_hours == 48
    assert cfg.validate() is True


def test_forecast_config_json_serialization(tmp_path: Path):
    """Test JSON serialization and deserialization."""
    cfg = ForecastConfig(model_name="WRF", forecast_hours=72, hpc_nodes=8)
    out_file = tmp_path / "fcst_config.json"

    cfg.to_json(filepath=str(out_file))
    assert out_file.exists()

    loaded = ForecastConfig.from_json(str(out_file))
    assert loaded.model_name == "WRF"
    assert loaded.forecast_hours == 72
    assert loaded.hpc_nodes == 8
