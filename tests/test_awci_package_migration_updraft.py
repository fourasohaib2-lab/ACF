"""Regression guard for Phase 7 of the AWCI separate-package migration
(2026-09-21, "continue avec updraft.py" - see
docs/architecture/acf_awci_architecture_gap_analysis.md's own "§2h"
section).

updraft.py (real max updraft velocity from CAPE, using
CloudDynamicsEngine) is the third and last of spatial_field.py's own
compute_real_<x>_at_point-style dependencies (after
convective_energy.py and theta_e.py in Phase 6) to join awci.hazards/.
"""

from __future__ import annotations

import importlib


def test_old_acf_awci_namespace_reexports_the_exact_same_real_module():
    old = importlib.import_module("acf.awci.updraft")
    new = importlib.import_module("awci.hazards.updraft")

    assert old.compute_real_max_updraft_velocity is new.compute_real_max_updraft_velocity


def test_spatial_field_reaches_updraft_as_a_real_hazards_sibling():
    import awci.complexity.spatial_field as spatial_module
    from awci.hazards.updraft import compute_real_max_updraft_velocity

    assert spatial_module.compute_real_max_updraft_velocity is compute_real_max_updraft_velocity


def test_spatial_field_no_longer_reaches_any_of_its_hazard_inputs_through_the_acf_awci_shim():
    """All 9 of spatial_field.py's real per-point hazard/thermo
    dependencies (ceiling/convective_energy/dust/hydrometeor_phase/
    microburst/theta_e/updraft/visibility/wind_shear) are now direct
    awci.hazards imports, not acf.awci shim bounces - locks in the
    cleanup is complete, not partial."""
    import inspect

    import awci.complexity.spatial_field as spatial_module

    source = inspect.getsource(spatial_module)
    import_lines = [line for line in source.splitlines() if line.startswith("from acf.awci.")]
    assert import_lines == [], f"spatial_field.py still bounces through acf.awci shims: {import_lines}"
