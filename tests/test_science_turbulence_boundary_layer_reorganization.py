"""Regression guard for Phase 6 of the ACF science/ per-domain
reorganization (2026-09-21, "continue avec turbulence/ et
boundary_layer/" - see
docs/architecture/acf_awci_architecture_gap_analysis.md's own "§4f"
section).

Two single flat modules moved into two new subpackages:
``wind_turbulence.py`` into ``acf.science.turbulence`` (the blueprint's
own ``science/turbulence/`` - real module name kept as-is, a real flat
shim exists since there is no self-naming collision) and
``boundary_layer.py`` into ``acf.science.boundary_layer`` (self-named
collision with its own package - per the rule established in
§4a-§4e, no flat shim; the package's own ``__init__.py`` re-exports
directly).
"""

from __future__ import annotations

import importlib

_TURBULENCE_NAMES = ["CATIndex", "JET_STREAM_THRESHOLD_M_S", "JetStream", "TKEProduction"]
_BOUNDARY_LAYER_NAMES = ["BowenRatio", "FrictionVelocity", "MoninObukhovLength", "PBLHeight", "VON_KARMAN"]


def test_wind_turbulence_shim_reexports_every_real_name_identically():
    old = importlib.import_module("acf.science.wind_turbulence")
    new = importlib.import_module("acf.science.turbulence.wind_turbulence")

    for name in _TURBULENCE_NAMES:
        assert hasattr(old, name), f"acf.science.wind_turbulence is missing {name!r}"
        assert getattr(old, name) is getattr(new, name)


def test_turbulence_package_reexports_every_real_name_identically():
    pkg = importlib.import_module("acf.science.turbulence")
    new = importlib.import_module("acf.science.turbulence.wind_turbulence")

    assert sorted(pkg.__all__) == sorted(_TURBULENCE_NAMES)
    for name in _TURBULENCE_NAMES:
        assert getattr(pkg, name) is getattr(new, name)


def test_boundary_layer_package_reexports_every_real_name_identically():
    pkg = importlib.import_module("acf.science.boundary_layer")
    mod = importlib.import_module("acf.science.boundary_layer.boundary_layer")

    assert sorted(pkg.__all__) == sorted(_BOUNDARY_LAYER_NAMES)
    for name in _BOUNDARY_LAYER_NAMES:
        assert hasattr(mod, name), f"acf.science.boundary_layer.boundary_layer is missing {name!r}"
        assert getattr(pkg, name) is getattr(mod, name)


def test_new_packages_are_real_top_level_reachable():
    import acf.science.boundary_layer
    import acf.science.turbulence

    assert acf.science.turbulence.__name__ == "acf.science.turbulence"
    assert acf.science.boundary_layer.__name__ == "acf.science.boundary_layer"


def test_boundary_layer_module_has_no_dead_flat_shim():
    """No src/acf/science/boundary_layer.py shim exists - it would be
    permanently shadowed by the acf.science.boundary_layer package,
    the same self-naming-collision bug already found and fixed for
    thermodynamics.py/stability.py/dynamics.py/constants.py/
    radiation.py in §4a-§4e."""
    import acf.science.boundary_layer as pkg

    assert pkg.__file__.endswith("__init__.py")


def test_already_migrated_awci_dependents_reach_the_moved_module_directly():
    """awci/hazards/cat_turbulence.py and
    awci/complexity/wind_classification.py (from the AWCI migration)
    depend on wind_turbulence.py, moved in this phase - locks in they
    were repointed to acf.science.turbulence.wind_turbulence directly
    rather than left resolving through the acf.science shim."""
    import awci.complexity.wind_classification as wind_classification_module
    import awci.hazards.cat_turbulence as cat_turbulence_module
    from acf.science.turbulence.wind_turbulence import CATIndex, JET_STREAM_THRESHOLD_M_S, JetStream

    assert cat_turbulence_module.CATIndex is CATIndex
    assert wind_classification_module.JetStream is JetStream
    assert wind_classification_module.JET_STREAM_THRESHOLD_M_S == JET_STREAM_THRESHOLD_M_S


def test_real_caller_of_boundary_layer_still_resolves_correctly():
    """laws/boundary_layer.py (a distinct, coincidentally same-named
    sibling module in the science.laws subpackage) and surface_fire.py
    both depend on boundary_layer.py - locks in they still resolve to
    the exact same real classes through the package, since the import
    path itself never changed for this phase, exactly like
    constants.py/radiation.py in §4d/§4e."""
    import acf.science.laws.boundary_layer as laws_boundary_layer_module
    import acf.science.surface_fire as surface_fire_module
    from acf.science.boundary_layer import BowenRatio, MoninObukhovLength

    assert laws_boundary_layer_module.MoninObukhovLength is MoninObukhovLength
    assert surface_fire_module.BowenRatio is BowenRatio
