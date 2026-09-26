import json
from pathlib import Path

import pytest

from acf.awci.ops.cloud_profile import DEFAULT_CLOUD_PROFILE_PATH, load_cloud_profile


def test_default_profile_loads_with_documented_values() -> None:
    p = load_cloud_profile()
    assert p.name == "cloud-v1" and p.sigma_low_mid == 0.8 and p.sigma_mid_high == 0.45
    assert p.layer_min_fraction == 0.125 and p.ceiling_max_base_m == 6000.0
    assert p.convection["capillatus_temp_k"] == 235.15 and p.convection["glaciation_temp_k"] == 253.15
    assert set(p.references) >= {"rh_critical", "sigma_bounds", "layer_min_fraction", "ceiling_max_base_m"}


@pytest.mark.parametrize("patch", [
    {"rh_critical": {"low": 1.2, "mid": 0.7, "high": 0.7}},
    {"sigma_bounds": {"low_mid": 0.4, "mid_high": 0.45}},
    {"convection": {}},
])
def test_invalid_profiles_rejected(tmp_path: Path, patch: dict) -> None:
    raw = json.loads(DEFAULT_CLOUD_PROFILE_PATH.read_text()) | patch
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(raw))
    with pytest.raises(ValueError):
        load_cloud_profile(path)


def test_realised_convection_conditions_are_parsed_and_validated(tmp_path) -> None:
    import json as _json
    from acf.awci.ops.cloud_profile import DEFAULT_CLOUD_PROFILE_PATH, load_cloud_profile as _load
    raw = _json.loads(DEFAULT_CLOUD_PROFILE_PATH.read_text())
    raw["convection"]["realised"] = {"precip_rate": [">=", 0.1], "column_condensate": [">=", 0.3]}
    path = tmp_path / "p.json"
    path.write_text(_json.dumps(raw))
    assert _load(path).convection_realised == {"precip_rate": (">=", 0.1), "column_condensate": (">=", 0.3)}
    for bad in ({"cape": [">=", 1]}, {"precip_rate": ["==", 1]}, {"precip_rate": [">=", "x"]}):
        raw["convection"]["realised"] = bad
        path.write_text(_json.dumps(raw))
        with pytest.raises(ValueError):
            _load(path)
    del raw["convection"]["realised"]
    path.write_text(_json.dumps(raw))
    assert _load(path).convection_realised == {}
