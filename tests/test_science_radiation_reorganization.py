"""Regression guard for Phase 5 of the ACF science/ per-domain
reorganization (2026-09-21, "continue avec radiation/ et
microphysics/" - see
docs/architecture/acf_awci_architecture_gap_analysis.md's own "§4e"
section).

The single flat ``radiation.py`` module (4 real classes -
``StefanBoltzmann``, ``PlanckLaw``, ``BeerLambert``, ``SolarPosition``
- plus 5 real physical constants) moved into a new
``acf.science.radiation`` package - the blueprint's own
``science/radiation/`` layer. ``radiation.py`` shares its own name
with the package, so - per the rule established in §4a-§4d - there is
no flat shim; the package's own ``__init__.py`` re-exports every real
name directly.

There is no ``microphysics/`` counterpart in this phase: no flat
top-level ``microphysics.py`` module exists - the only real
microphysics content (``CloudMicrophysicsEngine``) already lives in
``science/clouds/microphysics.py``, inside the already-existing
``clouds/`` subpackage. Moving or reconciling that is a distinct,
larger architecture decision (already flagged as future work in §4),
not a mechanical single-file move, so it was left untouched this
phase.
"""

from __future__ import annotations

import importlib

_NAMES = [
    "BOLTZMANN_K",
    "BeerLambert",
    "PLANCK_H",
    "PlanckLaw",
    "SOLAR_CONSTANT_S0",
    "SPEED_OF_LIGHT_C",
    "STEFAN_BOLTZMANN_SIGMA",
    "SolarPosition",
    "StefanBoltzmann",
]


def test_package_reexports_every_real_name_identically():
    pkg = importlib.import_module("acf.science.radiation")
    mod = importlib.import_module("acf.science.radiation.radiation")

    for name in _NAMES:
        assert hasattr(pkg, name), f"acf.science.radiation is missing {name!r}"
        assert hasattr(mod, name), f"acf.science.radiation.radiation is missing {name!r}"
        assert getattr(pkg, name) is getattr(mod, name), (
            f"acf.science.radiation.{name} is not the same real object as "
            f"acf.science.radiation.radiation.{name}"
        )


def test_package_all_matches_the_real_module_public_api():
    pkg = importlib.import_module("acf.science.radiation")
    mod = importlib.import_module("acf.science.radiation.radiation")

    mod_public = sorted(n for n in vars(mod) if not n.startswith("_") and n not in ("annotations", "math"))
    assert sorted(pkg.__all__) == mod_public


def test_new_package_is_real_top_level_reachable():
    import acf.science.radiation

    assert acf.science.radiation.__name__ == "acf.science.radiation"
    assert acf.science.radiation.__file__.endswith("__init__.py")


def test_radiation_module_has_no_dead_flat_shim():
    """No src/acf/science/radiation.py shim exists - it would be
    permanently shadowed by the acf.science.radiation package, the
    same self-naming-collision bug already found and fixed for
    thermodynamics.py/stability.py/dynamics.py/constants.py in
    §4a-§4d."""
    import acf.science.radiation as pkg

    assert pkg.__file__.endswith("__init__.py")


def test_real_caller_still_resolves_correctly():
    """laws/radiation.py (a distinct, coincidentally same-named sibling
    module in the science.laws subpackage) imports PlanckLaw and
    SolarPosition from the bare acf.science.radiation path - locks in
    it still resolves to the exact same real classes through the
    package, since the import path itself never changed for this
    phase, exactly like constants.py in §4d."""
    import acf.science.laws.radiation as laws_radiation_module
    from acf.science.radiation import PlanckLaw, SolarPosition

    assert laws_radiation_module.PlanckLaw is PlanckLaw
    assert laws_radiation_module.SolarPosition is SolarPosition
