"""Regression guard for Phase 3 of the AWCI separate-package migration
(2026-09-21, "continue avec spatial_field.py et vertical_field.py" -
see docs/architecture/acf_awci_architecture_gap_analysis.md's own
"§2d" section).

spatial_field.py (compute_real_complexity_field, the real 2D/3D per-
point AWCI field used by the map overlay) and vertical_field.py
(score_volume, the same complexity computation along a vertical
profile) physically moved from acf.awci.<module> to
awci.complexity.<module>, alongside calculator.py (Phase 2) which both
depend on directly. acf.awci.<module> is now a thin re-export. This
locks in that every old import path still resolves to the exact same
real object as the new one.
"""

from __future__ import annotations

import importlib

import pytest

_MIGRATED_FIELD_MODULES = ["spatial_field", "vertical_field"]


@pytest.mark.parametrize("module_name", _MIGRATED_FIELD_MODULES)
def test_old_acf_awci_namespace_reexports_the_exact_same_real_module(module_name):
    old = importlib.import_module(f"acf.awci.{module_name}")
    new = importlib.import_module(f"awci.complexity.{module_name}")

    new_public_names = [name for name in vars(new) if not name.startswith("_")]
    assert new_public_names, f"awci.complexity.{module_name} exports nothing real to check"
    for name in new_public_names:
        if name == "annotations":
            continue
        assert hasattr(old, name), f"acf.awci.{module_name} is missing real re-export {name!r}"
        assert getattr(old, name) is getattr(new, name), (
            f"acf.awci.{module_name}.{name} is not the same real object as "
            f"awci.complexity.{module_name}.{name} - the re-export is stale or duplicated"
        )


def test_spatial_field_reaches_the_migrated_calculator_and_hazards_as_siblings():
    """spatial_field.py now lives alongside calculator.py in
    awci.complexity/, and imports the already-migrated hazard modules
    (ceiling/dust/hydrometeor_phase/microburst/visibility/wind_shear)
    directly from awci.hazards rather than bouncing through the
    acf.awci shim - locks in it reaches the one real AWCICalculator
    and the one real hazard functions, not a stale copy."""
    from awci.complexity.calculator import AWCICalculator
    from awci.complexity.spatial_field import AWCICalculator as spatial_calc_ref
    from awci.hazards.dust import compute_real_dust_risk_at_point

    assert spatial_calc_ref is AWCICalculator

    import awci.complexity.spatial_field as spatial_module

    assert spatial_module.compute_real_dust_risk_at_point is compute_real_dust_risk_at_point


def test_vertical_field_reaches_the_migrated_calculator_as_a_sibling():
    from awci.complexity.calculator import AWCICalculator
    from awci.complexity.vertical_field import AWCICalculator as vertical_calc_ref

    assert vertical_calc_ref is AWCICalculator
