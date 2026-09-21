"""Regression guard for Phase 1 of the ACF science/ per-domain
reorganization (2026-09-21, "continue avec la réorganisation de
science/ et parameters/" - see
docs/architecture/acf_awci_architecture_gap_analysis.md's own "§4"
section).

21 flat modules moved from directly under ``acf.science`` into
``acf.science.thermodynamics`` - the blueprint's own "initial
atmospheric priority" subdomain. ``acf.science.<module>`` is now a
thin re-export for every one of them. This locks in that every old
import path still resolves to the exact same real object as the new
one.
"""

from __future__ import annotations

import importlib

import pytest

_MODULES = [
    "thermodynamics",
    "potential_temperature",
    "virtual_temperature",
    "virtual_potential_temperature",
    "equivalent_potential_temperature",
    "mixing_ratio",
    "saturation_mixing_ratio",
    "specific_humidity",
    "vapor_pressure",
    "saturation_vapor_pressure",
    "relative_humidity",
    "humidity",
    "air_density",
    "dewpoint",
    "wet_bulb_temperature",
    "moist_static_energy",
    "dry_static_energy",
    "hypsometric_equation",
    "geopotential_height",
    "pressure",
    "temperature",
]


@pytest.mark.parametrize("module_name", _MODULES)
def test_thermodynamics_modules_are_identical(module_name):
    old = importlib.import_module(f"acf.science.{module_name}")
    new = importlib.import_module(f"acf.science.thermodynamics.{module_name}")

    new_public_names = [name for name in vars(new) if not name.startswith("_")]
    assert new_public_names, f"acf.science.thermodynamics.{module_name} exports nothing real to check"
    for name in new_public_names:
        if name == "annotations":
            continue
        assert hasattr(old, name), f"acf.science.{module_name} is missing real re-export {name!r}"
        assert getattr(old, name) is getattr(new, name), (
            f"acf.science.{module_name}.{name} is not the same real object as "
            f"acf.science.thermodynamics.{module_name}.{name} - the re-export is stale or duplicated"
        )


def test_new_package_is_real_top_level_reachable():
    import acf.science.thermodynamics

    assert acf.science.thermodynamics.__name__ == "acf.science.thermodynamics"


def test_package_reexports_its_own_real_public_api():
    import acf.science.thermodynamics as pkg

    assert pkg.__all__
    for name in pkg.__all__:
        assert hasattr(pkg, name), f"acf.science.thermodynamics is missing {name!r} in its own namespace"


def test_internal_cross_reference_uses_the_new_package_directly():
    """equivalent_potential_temperature.py depends on
    saturation_mixing_ratio.py and saturation_vapor_pressure.py, both
    moved in this same phase - locks in it now imports them directly
    within acf.science.thermodynamics, not through the shim."""
    import acf.science.thermodynamics.equivalent_potential_temperature as module
    from acf.science.thermodynamics.saturation_mixing_ratio import SaturationMixingRatio
    from acf.science.thermodynamics.saturation_vapor_pressure import SaturationVaporPressure

    assert module.SaturationMixingRatio is SaturationMixingRatio
    assert module.SaturationVaporPressure is SaturationVaporPressure


def test_already_migrated_awci_dependents_reach_the_moved_modules_directly():
    """Several already-migrated awci.* modules (Phases 1-10) depend on
    thermodynamics modules moved in this phase - locks in they were
    repointed to acf.science.thermodynamics.* directly rather than left
    resolving through the acf.science shim."""
    import awci.complexity.metar_verification as metar_verification_module
    import awci.complexity.workstation_fields as workstation_fields_module
    import awci.hazards.ceiling as ceiling_module
    import awci.hazards.dust as dust_module
    import awci.hazards.hydrometeor_phase as hydrometeor_phase_module
    import awci.hazards.theta_e as theta_e_module
    import awci.hazards.visibility as visibility_module
    from acf.science.thermodynamics.dewpoint import DewPoint
    from acf.science.thermodynamics.potential_temperature import PotentialTemperature
    from acf.science.thermodynamics.saturation_mixing_ratio import SaturationMixingRatio
    from acf.science.thermodynamics.saturation_vapor_pressure import SaturationVaporPressure
    from acf.science.thermodynamics.thermodynamics import Thermodynamics

    assert visibility_module.Thermodynamics is Thermodynamics
    assert theta_e_module.Thermodynamics is Thermodynamics
    assert theta_e_module.DewPoint is DewPoint
    assert hydrometeor_phase_module.Thermodynamics is Thermodynamics
    assert dust_module.Thermodynamics is Thermodynamics
    assert ceiling_module.Thermodynamics is Thermodynamics
    assert ceiling_module.DewPoint is DewPoint
    assert metar_verification_module.SaturationMixingRatio is SaturationMixingRatio
    assert metar_verification_module.SaturationVaporPressure is SaturationVaporPressure
    assert workstation_fields_module.PotentialTemperature is PotentialTemperature
