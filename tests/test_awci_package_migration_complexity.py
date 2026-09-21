"""Regression guard for Phase 2 of the AWCI separate-package migration
(2026-09-21, "continue avec calculator.py" - see
docs/architecture/acf_awci_architecture_gap_analysis.md's own "§2c"
section).

The AWCI complexity engine (AWCICalculator, WeightsManager,
Normalizer, and the shared scientific_status classification types)
physically moved from acf.awci.<module> to awci.complexity.<module>;
acf.awci.<module> is now a thin `from awci.complexity.<module> import
*` re-export. This locks in that every old import path still resolves
to the exact same real object as the new one - not a copy, not a
re-implementation - so existing callers (57 real files importing
calculator.py alone, 48 test files touching this engine, verified by
grep before this migration started) keep working unchanged.
"""

from __future__ import annotations

import importlib

import pytest

_MIGRATED_COMPLEXITY_MODULES = [
    "scientific_status",
    "normalizer",
    "weights",
    "calculator",
]


@pytest.mark.parametrize("module_name", _MIGRATED_COMPLEXITY_MODULES)
def test_old_acf_awci_namespace_reexports_the_exact_same_real_module(module_name):
    """acf.awci.<module> and awci.complexity.<module> must be the SAME
    module object (re-exported), not two independent copies that
    could silently drift apart."""
    old = importlib.import_module(f"acf.awci.{module_name}")
    new = importlib.import_module(f"awci.complexity.{module_name}")

    new_public_names = [name for name in vars(new) if not name.startswith("_")]
    assert new_public_names, f"awci.complexity.{module_name} exports nothing real to check"
    for name in new_public_names:
        if name == "annotations":  # from __future__ import annotations leaks into vars()
            continue
        assert hasattr(old, name), f"acf.awci.{module_name} is missing real re-export {name!r}"
        assert getattr(old, name) is getattr(new, name), (
            f"acf.awci.{module_name}.{name} is not the same real object as "
            f"awci.complexity.{module_name}.{name} - the re-export is stale or duplicated"
        )


def test_package_level_reexports_also_point_at_the_new_real_objects():
    """acf.awci's own __init__.py re-exports AWCICalculator/Normalizer/
    WeightsManager via relative imports (`.calculator`) - those must
    resolve through the shim to the exact same real classes the new
    awci.complexity namespace defines."""
    from acf.awci import AWCICalculator as pkg_calc
    from acf.awci import Normalizer as pkg_norm
    from acf.awci import WeightsManager as pkg_weights
    from awci.complexity.calculator import AWCICalculator
    from awci.complexity.normalizer import Normalizer
    from awci.complexity.weights import WeightsManager

    assert pkg_calc is AWCICalculator
    assert pkg_norm is Normalizer
    assert pkg_weights is WeightsManager


def test_calculator_still_constructs_and_uses_the_real_dependency_chain():
    """End-to-end sanity: AWCICalculator() must still construct through
    its real scientific_status -> normalizer/weights -> calculator
    dependency chain, now spread across 3 new-package sibling modules
    instead of 3 same-directory ones."""
    from acf.awci.calculator import AWCICalculator

    calc = AWCICalculator()
    assert calc is not None


def test_hazards_modules_still_reach_the_moved_normalizer_through_the_shim():
    """awci.hazards.microburst (Phase 1) imports Normalizer from
    acf.awci.normalizer - that module is now itself a Phase 2 shim, so
    this locks in the shim-of-a-shim chain resolves to the real class,
    not a stale copy."""
    import awci.hazards.microburst as microburst_module
    from awci.complexity.normalizer import Normalizer

    assert microburst_module.Normalizer is Normalizer
