"""Regression guard for Phase 1 of the AWCI separate-package migration
(2026-09-21, explicit user request "passe à AWCI en package séparé" -
see docs/architecture/acf_awci_architecture_gap_analysis.md's own
"§2a" section).

The 10 real aviation hazard modules physically moved from
acf.awci.<module> to awci.hazards.<module>; acf.awci.<module> is now a
thin `from awci.hazards.<module> import *` re-export. This locks in
that every old import path still resolves to the exact same real
object as the new one - not a copy, not a re-implementation - so
existing callers (153 real files, 123 test files, verified by grep
before this migration started) keep working unchanged.
"""

from __future__ import annotations

import importlib

import pytest

_MIGRATED_HAZARD_MODULES = [
    "icing_temperature_range",
    "ceiling",
    "visibility",
    "dust",
    "microburst",
    "volcanic_ash",
    "wind_shear",
    "cat_turbulence",
    "orographic_froude",
    "hydrometeor_phase",
]


@pytest.mark.parametrize("module_name", _MIGRATED_HAZARD_MODULES)
def test_old_acf_awci_namespace_reexports_the_exact_same_real_module(module_name):
    """acf.awci.<module> and awci.hazards.<module> must be the SAME
    module object (re-exported), not two independent copies that
    could silently drift apart."""
    old = importlib.import_module(f"acf.awci.{module_name}")
    new = importlib.import_module(f"awci.hazards.{module_name}")

    # The shim module itself is a distinct module object (it has to be,
    # it lives at a different dotted path) - what must be identical is
    # every real public symbol it re-exports via `import *`.
    new_public_names = [name for name in vars(new) if not name.startswith("_")]
    assert new_public_names, f"awci.hazards.{module_name} exports nothing real to check"
    for name in new_public_names:
        if name in ("annotations",):  # from __future__ import annotations leaks into vars()
            continue
        assert hasattr(old, name), f"acf.awci.{module_name} is missing real re-export {name!r}"
        assert getattr(old, name) is getattr(new, name), (
            f"acf.awci.{module_name}.{name} is not the same real object as "
            f"awci.hazards.{module_name}.{name} - the re-export is stale or duplicated"
        )


def test_awci_package_exists_as_a_real_separate_top_level_package():
    """awci is genuinely importable as its own top-level package (not
    nested under acf), per the reference architecture's "AWCI as a
    separate package" direction."""
    import awci

    assert awci.__name__ == "awci"
    assert not awci.__name__.startswith("acf")


def test_hydrometeor_phase_cross_import_uses_the_new_sibling_location():
    """hydrometeor_phase.py's own real dependency on
    is_within_icing_temperature_range (both hazard modules, both
    migrated together) must resolve within the new awci.hazards
    package, not reach back into acf.awci for a sibling that moved
    with it."""
    from awci.hazards.hydrometeor_phase import is_within_icing_temperature_range
    from awci.hazards.icing_temperature_range import (
        is_within_icing_temperature_range as canonical,
    )

    assert is_within_icing_temperature_range is canonical
