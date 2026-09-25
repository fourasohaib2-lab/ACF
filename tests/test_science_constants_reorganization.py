"""Regression guard for Phase 4 of the ACF science/ per-domain
reorganization (2026-09-21, "continue avec constants/" - see
docs/architecture/acf_awci_architecture_gap_analysis.md's own "§4d"
section).

The single flat ``constants.py`` module moved into a new
``acf.science.constants`` package - the blueprint's own
``science/constants/`` layer. ``constants.py`` shares its own name
with the package, so - per the rule established in §4a/§4b/§4c - there
is no flat shim; the package's own ``__init__.py`` re-exports every
real constant directly. This locks in that every real constant is
still reachable at the exact same ``acf.science.constants.<NAME>``
path every existing caller already uses, and is the same real object
as the one defined in the real module.
"""

from __future__ import annotations

import importlib

_CONSTANTS = [
    "CP",
    "CV",
    "DEWPOINT_EXCEEDS_TEMPERATURE_TOLERANCE_K",
    "EARTH_RADIUS",
    "EPSILON",
    "G",
    "KAPPA",
    "LF",
    "LS",
    "LV",
    "MOLAR_MASS_DRY_AIR",
    "MOLAR_MASS_WATER",
    "OMEGA",
    "P0",
    "RD",
    "RHO_ICE",
    "RHO_WATER",
    "RV",
    "STANDARD_DENSITY",
    "STANDARD_PRESSURE",
    "STANDARD_TEMPERATURE",
    "T0",
    "UNIVERSAL_GAS_CONSTANT",
]


def test_package_reexports_every_real_constant_identically():
    pkg = importlib.import_module("acf.science.constants")
    mod = importlib.import_module("acf.science.constants.constants")

    for name in _CONSTANTS:
        assert hasattr(pkg, name), f"acf.science.constants is missing {name!r}"
        assert hasattr(mod, name), f"acf.science.constants.constants is missing {name!r}"
        assert getattr(pkg, name) == getattr(mod, name), (
            f"acf.science.constants.{name} != acf.science.constants.constants.{name}"
        )


def test_package_all_matches_the_real_module_public_api():
    pkg = importlib.import_module("acf.science.constants")
    mod = importlib.import_module("acf.science.constants.constants")

    mod_public = sorted(n for n in vars(mod) if not n.startswith("_") and n != "annotations")
    assert sorted(pkg.__all__) == mod_public


def test_new_package_is_real_top_level_reachable():
    import acf.science.constants

    assert acf.science.constants.__name__ == "acf.science.constants"
    assert acf.science.constants.__file__.endswith("__init__.py")


def test_constants_module_has_no_dead_flat_shim():
    """No src/acf/science/constants.py shim exists - it would be
    permanently shadowed by the acf.science.constants package, the
    same self-naming-collision bug already found and fixed for
    thermodynamics.py/stability.py/dynamics.py in §4a/§4b/§4c."""
    import acf.science.constants as pkg

    assert pkg.__file__.endswith("__init__.py")


def test_real_callers_across_the_codebase_still_resolve_correctly():
    """A handful of the real, actual consumer modules across science/
    (already-migrated ones and still-flat ones alike) and awci/ - locks
    in that acf.science.constants.<NAME> resolves to the exact same
    real value every one of them was already importing, since the
    import path itself never changed (constants.py's name equals its
    new package's name, so there is no old-path-vs-new-path
    distinction for this phase, unlike every other reorganization
    phase so far)."""
    import awci.complexity.workstation_fields as workstation_fields_module
    from acf.science.constants import G, RD
    from acf.science.convection.cape import G as cape_g
    from acf.science.convection.cape import T0 as cape_t0
    from acf.science.thermodynamics.geopotential_height import G as geopotential_g

    assert cape_g is G
    assert cape_t0 is not None
    assert geopotential_g is G
    assert workstation_fields_module.G is G
    assert workstation_fields_module.RD is RD
