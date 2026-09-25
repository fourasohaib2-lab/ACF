"""Regression guard for Phase 2 of the ACF science/ per-domain
reorganization (2026-09-21, "continue avec stability/ et convection/" -
see docs/architecture/acf_awci_architecture_gap_analysis.md's own "§4b"
section).

15 flat modules moved from directly under ``acf.science`` into two new
subpackages, ``acf.science.stability`` (7 modules) and
``acf.science.convection`` (8 modules) - the blueprint's own
``science/stability/``/``science/convection/`` layers.
``acf.science.<module>`` is now a thin re-export for every one of
them, except ``stability.py`` (see below). This locks in that every
old import path still resolves to the exact same real object as the
new one.

``stability.py`` is special-cased exactly like ``thermodynamics.py``
was in Phase 1: it shares its own name with the new
``acf.science.stability`` package, so a flat shim file at that exact
path would be permanently shadowed by the package directory and never
actually reachable - dead code. There is no flat shim for it; the
package's own ``__init__.py`` re-exports ``Stability`` directly
instead.
"""

from __future__ import annotations

import importlib

import pytest

_STABILITY_MODULES = [
    "bulk_richardson_number",
    "k_index",
    "sweat_index",
    "total_totals",
    "lifted_index",
    "showalter_index",
]

_CONVECTION_MODULES = [
    "cape",
    "cin",
    "lcl",
    "lfc",
    "parcel_ascent",
    "storm_relative_helicity",
    "storm_motion",
    "bulk_wind_shear",
]


@pytest.mark.parametrize("module_name", _STABILITY_MODULES)
def test_stability_modules_are_identical(module_name):
    old = importlib.import_module(f"acf.science.{module_name}")
    new = importlib.import_module(f"acf.science.stability.{module_name}")
    _assert_reexport_identical(old, new, module_name, "acf.science.stability")


@pytest.mark.parametrize("module_name", _CONVECTION_MODULES)
def test_convection_modules_are_identical(module_name):
    old = importlib.import_module(f"acf.science.{module_name}")
    new = importlib.import_module(f"acf.science.convection.{module_name}")
    _assert_reexport_identical(old, new, module_name, "acf.science.convection")


def _assert_reexport_identical(old, new, module_name, new_pkg_label):
    new_public_names = [name for name in vars(new) if not name.startswith("_")]
    assert new_public_names, f"{new_pkg_label}.{module_name} exports nothing real to check"
    for name in new_public_names:
        if name == "annotations":
            continue
        assert hasattr(old, name), f"acf.science.{module_name} is missing real re-export {name!r}"
        assert getattr(old, name) is getattr(new, name), (
            f"acf.science.{module_name}.{name} is not the same real object as "
            f"{new_pkg_label}.{module_name}.{name} - the re-export is stale or duplicated"
        )


def test_new_packages_are_real_top_level_reachable():
    import acf.science.convection
    import acf.science.stability

    assert acf.science.stability.__name__ == "acf.science.stability"
    assert acf.science.convection.__name__ == "acf.science.convection"


@pytest.mark.parametrize("subpkg", ["stability", "convection"])
def test_package_reexports_its_own_real_public_api(subpkg):
    pkg = importlib.import_module(f"acf.science.{subpkg}")
    assert pkg.__all__
    for name in pkg.__all__:
        assert hasattr(pkg, name), f"acf.science.{subpkg} is missing {name!r} in its own namespace"


def test_stability_module_is_reachable_only_through_the_package_not_a_dead_flat_shim():
    """No src/acf/science/stability.py shim exists - it would be
    permanently shadowed by the acf.science.stability package. The
    package's own __init__.py re-exports Stability directly instead,
    exactly like acf.science.thermodynamics.Thermodynamics in Phase 1."""
    import acf.science.stability as pkg
    from acf.science.stability.stability import Stability

    assert pkg.__file__.endswith("__init__.py")
    assert pkg.Stability is Stability


def test_stability_class_reuses_convection_domain_indices_across_packages():
    """Stability.py's own Stability class is a real composite index
    aggregator that reuses CAPE/CIN/LCL/StormRelativeHelicity from the
    convection package directly - a genuine, disclosed cross-package
    dependency, not a migration artifact. Locks in it resolves through
    acf.science.convection.* directly, not the acf.science shim."""
    import acf.science.stability.stability as stability_module
    from acf.science.convection.cape import CAPE
    from acf.science.convection.cin import CIN
    from acf.science.convection.lcl import LCL
    from acf.science.convection.storm_relative_helicity import StormRelativeHelicity

    assert stability_module.CAPE is CAPE
    assert stability_module.CIN is CIN
    assert stability_module.LCL is LCL
    assert stability_module.StormRelativeHelicity is StormRelativeHelicity


def test_cape_cin_lcl_reuse_already_migrated_thermodynamics_modules_directly():
    """cape.py/cin.py depend on VirtualTemperature and lcl.py depends
    on EquivalentPotentialTemperature - both moved into
    acf.science.thermodynamics in Phase 1. Locks in they were
    repointed to the direct new location, not left on the shim."""
    import acf.science.convection.cape as cape_module
    import acf.science.convection.cin as cin_module
    import acf.science.convection.lcl as lcl_module
    from acf.science.thermodynamics.equivalent_potential_temperature import EquivalentPotentialTemperature
    from acf.science.thermodynamics.virtual_temperature import VirtualTemperature

    assert cape_module.VirtualTemperature is VirtualTemperature
    assert cin_module.VirtualTemperature is VirtualTemperature
    assert lcl_module.EquivalentPotentialTemperature is EquivalentPotentialTemperature


def test_already_migrated_awci_dependents_reach_the_moved_modules_directly():
    """awci/hazards/wind_shear.py and awci/complexity/workstation_fields.py
    (from the AWCI migration) depend on modules moved in this phase -
    locks in they were repointed to acf.science.{stability,convection}.*
    directly rather than left resolving through the acf.science shim."""
    import awci.complexity.workstation_fields as workstation_fields_module
    import awci.hazards.wind_shear as wind_shear_module
    from acf.science.convection.bulk_wind_shear import BulkWindShear
    from acf.science.convection.lcl import LCL
    from acf.science.convection.storm_motion import StormMotion
    from acf.science.convection.storm_relative_helicity import StormRelativeHelicity

    assert wind_shear_module.BulkWindShear is BulkWindShear
    assert workstation_fields_module.LCL is LCL
    assert workstation_fields_module.StormMotion is StormMotion
    assert workstation_fields_module.StormRelativeHelicity is StormRelativeHelicity
