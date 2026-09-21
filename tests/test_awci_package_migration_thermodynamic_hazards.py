"""Regression guard for Phase 6 of the AWCI separate-package migration
(2026-09-21, "continue avec convective_energy.py et theta_e.py" - see
docs/architecture/acf_awci_architecture_gap_analysis.md's own "§2g"
section).

convective_energy.py (real per-point CAPE/CIN) and theta_e.py (real
per-point equivalent potential temperature) follow the exact same
compute_real_<x>_at_point pattern as the 10 hazard modules migrated in
Phase 1, and are consumed by spatial_field.py the same way - so both
joined awci.hazards/ rather than awci.complexity/.
"""

from __future__ import annotations

import importlib

import pytest

_MIGRATED_THERMO_MODULES = ["convective_energy", "theta_e"]


@pytest.mark.parametrize("module_name", _MIGRATED_THERMO_MODULES)
def test_old_acf_awci_namespace_reexports_the_exact_same_real_module(module_name):
    old = importlib.import_module(f"acf.awci.{module_name}")
    new = importlib.import_module(f"awci.hazards.{module_name}")

    new_public_names = [name for name in vars(new) if not name.startswith("_")]
    assert new_public_names, f"awci.hazards.{module_name} exports nothing real to check"
    for name in new_public_names:
        if name == "annotations":
            continue
        assert hasattr(old, name), f"acf.awci.{module_name} is missing real re-export {name!r}"
        assert getattr(old, name) is getattr(new, name), (
            f"acf.awci.{module_name}.{name} is not the same real object as "
            f"awci.hazards.{module_name}.{name} - the re-export is stale or duplicated"
        )


def test_spatial_field_reaches_convective_energy_and_theta_e_as_real_hazards_siblings():
    """spatial_field.py (awci.complexity/) now imports both directly
    from awci.hazards/ as cross-package siblings, not through the
    acf.awci shim - locks in it reaches the one real function, not a
    stale copy."""
    import awci.complexity.spatial_field as spatial_module
    from awci.hazards.convective_energy import compute_real_cape_cin_at_point
    from awci.hazards.theta_e import compute_real_theta_e_at_point

    assert spatial_module.compute_real_cape_cin_at_point is compute_real_cape_cin_at_point
    assert spatial_module.compute_real_theta_e_at_point is compute_real_theta_e_at_point
