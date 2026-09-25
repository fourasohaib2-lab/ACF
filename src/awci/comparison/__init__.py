"""AWCI multi-model comparison and fusion.

Migrated 2026-09-21 (Phase 8 of the AWCI separate-package migration -
see ``awci``'s own package docstring and
``docs/architecture/acf_awci_architecture_gap_analysis.md``) from
``acf.awci``. Real generic grid regridding and full-field multi-model
fusion - the blueprint's own ``awci/comparison/`` layer, started with
its first real modules. Distinct from
``acf.visualization.ai_forecast_center.model_consensus_engine`` (real,
non-GUI, already independently reachable - see the gap analysis's own
"corrected 2026-09-21" note on why that one was NOT moved here).
"""
