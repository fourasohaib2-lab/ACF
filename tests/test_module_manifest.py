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


def test_module_manifest_unassessed_defaults():
    """
    CORRECTED: maturity/test_coverage_pct/doc_coverage_pct used to
    default to MaturityLevel.PRODUCTION/100.0/100.0 - the best possible
    score on every axis - for any manifest not explicitly measured.
    """
    manifest = ModuleManifest(name="unmeasured_module")
    assert manifest.maturity == MaturityLevel.UNASSESSED
    assert manifest.test_coverage_pct is None
    assert manifest.doc_coverage_pct is None


def test_registry_manager_no_manifests_found_is_honestly_empty(tmp_path: Path):
    """
    CORRECTED: when no module.yaml files exist anywhere (genuinely the
    case throughout this repository), scan_workspace() used to
    silently fabricate 5 specific named modules claiming
    PRODUCTION/STABLE maturity and 100%/100% test/doc coverage -
    feeding a fake "maturity summary matrix" straight to the ESOC
    display with zero real manifest ever read from disk.
    """
    manager = ModuleRegistryManager(root_dir=tmp_path)
    assert manager.get_summary_matrix() == []


def test_registry_manager_logs_a_broken_manifest_instead_of_silently_dropping_it(tmp_path, caplog):
    """
    CORRECTED (2026-09-05 audit de continuation): a module.yaml that
    exists but fails to parse used to be swallowed by a bare
    `except Exception: pass` and treated identically to "no manifest at
    all" - same class of bug as hpc_workflow/workflow_configuration.py
    (fixed in the 2026-09-02 sweep, before this file existed). A broken
    manifest must now be logged, not silently dropped.
    """
    broken = tmp_path / "broken_module" / "module.yaml"
    broken.parent.mkdir(parents=True)
    broken.write_text("name: [this is not valid YAML for a mapping: :", encoding="utf-8")

    with caplog.at_level("WARNING", logger="acf.master.module_manifest"):
        manager = ModuleRegistryManager(root_dir=tmp_path)

    assert manager.get_summary_matrix() == []
    assert any("broken_module" in record.getMessage() or str(broken) in record.getMessage() for record in caplog.records)
