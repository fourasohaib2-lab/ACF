"""Regression guard for Phase 3 of the ACF science/ per-domain
reorganization (2026-09-21, "continue avec dynamics/" - see
docs/architecture/acf_awci_architecture_gap_analysis.md's own "§4c"
section).

6 flat modules moved from directly under ``acf.science`` into
``acf.science.dynamics`` - the blueprint's own ``science/dynamics/``
layer. ``acf.science.<module>`` is now a thin re-export for every one
of them, except ``dynamics.py`` (see below). This locks in that every
old import path still resolves to the exact same real object as the
new one.

``dynamics.py`` is special-cased exactly like ``thermodynamics.py``
(§4a) and ``stability.py`` (§4b): it shares its own name with the new
``acf.science.dynamics`` package, so a flat shim file at that exact
path would be permanently shadowed by the package directory - dead
code. There is no flat shim for it; the package's own ``__init__.py``
re-exports ``Dynamics`` directly instead.
"""

from __future__ import annotations

import importlib

import pytest

_MODULES = [
    "divergence",
    "vorticity",
    "frontogenesis",
    "fronts",
    "potential_vorticity",
]


@pytest.mark.parametrize("module_name", _MODULES)
def test_dynamics_modules_are_identical(module_name):
    old = importlib.import_module(f"acf.science.{module_name}")
    new = importlib.import_module(f"acf.science.dynamics.{module_name}")

    new_public_names = [name for name in vars(new) if not name.startswith("_")]
    assert new_public_names, f"acf.science.dynamics.{module_name} exports nothing real to check"
    for name in new_public_names:
        if name == "annotations":
            continue
        assert hasattr(old, name), f"acf.science.{module_name} is missing real re-export {name!r}"
        assert getattr(old, name) is getattr(new, name), (
            f"acf.science.{module_name}.{name} is not the same real object as "
            f"acf.science.dynamics.{module_name}.{name} - the re-export is stale or duplicated"
        )


def test_new_package_is_real_top_level_reachable():
    import acf.science.dynamics

    assert acf.science.dynamics.__name__ == "acf.science.dynamics"


def test_package_reexports_its_own_real_public_api():
    import acf.science.dynamics as pkg

    assert pkg.__all__
    for name in pkg.__all__:
        assert hasattr(pkg, name), f"acf.science.dynamics is missing {name!r} in its own namespace"


def test_dynamics_module_is_reachable_only_through_the_package_not_a_dead_flat_shim():
    """No src/acf/science/dynamics.py shim exists - it would be
    permanently shadowed by the acf.science.dynamics package. The
    package's own __init__.py re-exports Dynamics directly instead,
    exactly like Thermodynamics (§4a) and Stability (§4b)."""
    import acf.science.dynamics as pkg
    from acf.science.dynamics.dynamics import Dynamics

    assert pkg.__file__.endswith("__init__.py")
    assert pkg.Dynamics is Dynamics


def test_dynamics_class_reuses_already_migrated_thermodynamics_modules_directly():
    """dynamics.py's own Dynamics class depends on GeopotentialHeight
    and HypsometricEquation, both moved into acf.science.thermodynamics
    in Phase 1 (§4a). Locks in it resolves them directly, not through
    the acf.science shim."""
    import acf.science.dynamics.dynamics as dynamics_module
    from acf.science.thermodynamics.geopotential_height import GeopotentialHeight
    from acf.science.thermodynamics.hypsometric_equation import HypsometricEquation

    assert dynamics_module.GeopotentialHeight is GeopotentialHeight
    assert dynamics_module.HypsometricEquation is HypsometricEquation


def test_already_migrated_awci_dependent_reaches_the_moved_module_directly():
    """awci/complexity/workstation_fields.py (from the AWCI migration)
    depends on Divergence, moved in this phase - locks in it was
    repointed to acf.science.dynamics.divergence directly rather than
    left resolving through the acf.science shim."""
    import awci.complexity.workstation_fields as workstation_fields_module
    from acf.science.dynamics.divergence import Divergence

    assert workstation_fields_module.Divergence is Divergence
