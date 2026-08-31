"""
Unit test suite for ModuleManifest and ModuleRegistryManager (ACF-1000).
"""

from pathlib import Path

from acf.master.module_manifest import MaturityLevel, ModuleManifest, ModuleRegistryManager


def test_module_manifest_serialization(tmp_path: Path):
    """Test serializing and deserializing module.yaml manifest."""
    manifest = ModuleManifest(
        name="hpc_connector",
        owner="Chief HPC Architect",
        version="2.1.0",
        maturity=MaturityLevel.PRODUCTION,
        test_coverage_pct=100.0,
    )

    out_file = tmp_path / "module.yaml"
    manifest.to_yaml(out_file)
    assert out_file.exists()

    loaded = ModuleManifest.from_yaml(out_file)
    assert loaded.name == "hpc_connector"
    assert loaded.maturity == MaturityLevel.PRODUCTION
    assert loaded.test_coverage_pct == 100.0


def test_module_registry_manager(tmp_path: Path):
    """Test registry manager workspace scanning."""
    m1 = ModuleManifest(name="mod1", maturity=MaturityLevel.STABLE)
    m1.to_yaml(tmp_path / "mod1" / "module.yaml")

    manager = ModuleRegistryManager(root_dir=tmp_path)
    summary = manager.get_summary_matrix()
    assert len(summary) >= 1
    assert summary[0]["name"] == "mod1"
    assert summary[0]["maturity"] == "Stable"
