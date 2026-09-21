"""Regression guard for Phase 5 of the AWCI separate-package migration
(2026-09-21, "continue avec scale_classification.py et
wind_classification.py" - see
docs/architecture/acf_awci_architecture_gap_analysis.md's own "§2f"
section).

Both modules were fully self-contained (zero acf.awci sibling
dependencies) and map directly onto the blueprint's own
awci/complexity/classification.py concept, so both joined
awci.complexity/ alongside calculator.py and friends.
"""

from __future__ import annotations

import importlib

import pytest

_MIGRATED_CLASSIFICATION_MODULES = ["scale_classification", "wind_classification"]


@pytest.mark.parametrize("module_name", _MIGRATED_CLASSIFICATION_MODULES)
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
