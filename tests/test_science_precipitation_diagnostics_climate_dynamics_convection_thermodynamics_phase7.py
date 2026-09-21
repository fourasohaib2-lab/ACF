"""Regression guard for Phase 7 of the ACF science/ per-domain
reorganization (2026-09-21, "continue pour tout" - see
docs/architecture/acf_awci_architecture_gap_analysis.md's own "§4g"
section).

Eight flat modules moved in one batch, three into brand-new
subpackages and five joining already-existing ones from earlier
phases:
- science/precipitation/ (new): precipitation.py - self-named
  collision, package-only re-export.
- science/diagnostics/ (new): diagnostics.py - self-named collision,
  package-only re-export.
- science/climate/ (new): climatology.py - no collision, real flat
  shim kept.
- science/dynamics/ (extended, §4c): synoptic.py, cyclones.py,
  wind.py - no collision, real flat shims kept.
- science/convection/ (extended, §4b): severe_weather.py - no
  collision, real flat shim kept.
- science/thermodynamics/ (extended, §4a): moisture.py - no
  collision, real flat shim kept.
"""

from __future__ import annotations

import importlib

# (old flat name, new subpackage, names to check via the package's own __all__)
_SELF_COLLISION = {
    "precipitation": ("precipitation", ["ECHO_TOP_THRESHOLD_DBZ", "EchoTop", "HydrometeorType", "PrecipitationIntensity", "VIL"]),
    "diagnostics": ("diagnostics", ["DiagnosticAlert", "SituationDiagnosis"]),
}

# (old flat name, new subpackage, real names defined in that module)
_REAL_SHIM = {
    "climatology": ("climate", ["ClimatologicalRecord", "Climatology", "HeatColdWave"]),
    "synoptic": ("dynamics", ["Coriolis", "EARTH_RADIUS_M", "ErtelPotentialVorticity", "GeostrophicWind", "ThermalWind"]),
    "cyclones": ("dynamics", ["BOMB_REFERENCE_LATITUDE_DEG", "Bombogenesis", "BruntVaisalaFrequency", "GradientWind", "RossbyRadius", "SaffirSimpson"]),
    "wind": ("dynamics", ["Wind"]),
    "severe_weather": ("convection", ["SevereWeather"]),
    "moisture": ("thermodynamics", ["Moisture"]),
}


def test_self_collision_packages_reexport_every_real_name():
    for mod, (subpkg, names) in _SELF_COLLISION.items():
        pkg = importlib.import_module(f"acf.science.{subpkg}")
        real = importlib.import_module(f"acf.science.{subpkg}.{mod}")
        assert sorted(pkg.__all__) == sorted(names), f"{subpkg} __all__ mismatch"
        for name in names:
            assert hasattr(pkg, name), f"acf.science.{subpkg} missing {name!r}"
            assert getattr(pkg, name) is getattr(real, name)


def test_self_collision_packages_have_no_dead_flat_shim():
    """precipitation.py and diagnostics.py each share their own name
    with their new package - no flat shim exists for either, the same
    self-naming-collision rule established in §4a-§4f."""
    import acf.science.diagnostics as diagnostics_pkg
    import acf.science.precipitation as precipitation_pkg

    assert precipitation_pkg.__file__.endswith("__init__.py")
    assert diagnostics_pkg.__file__.endswith("__init__.py")


def test_real_shim_modules_reexport_every_real_name_identically():
    for mod, (subpkg, names) in _REAL_SHIM.items():
        old = importlib.import_module(f"acf.science.{mod}")
        new = importlib.import_module(f"acf.science.{subpkg}.{mod}")
        for name in names:
            assert hasattr(old, name), f"acf.science.{mod} is missing real re-export {name!r}"
            assert getattr(old, name) is getattr(new, name), (
                f"acf.science.{mod}.{name} is not the same real object as "
                f"acf.science.{subpkg}.{mod}.{name}"
            )


def test_extended_packages_own_all_includes_the_new_phase7_names():
    dynamics_names = [
        "Coriolis", "EARTH_RADIUS_M", "ErtelPotentialVorticity", "GeostrophicWind", "ThermalWind",
        "BOMB_REFERENCE_LATITUDE_DEG", "Bombogenesis", "BruntVaisalaFrequency", "GradientWind",
        "RossbyRadius", "SaffirSimpson", "Wind",
    ]
    dynamics_pkg = importlib.import_module("acf.science.dynamics")
    for name in dynamics_names:
        assert name in dynamics_pkg.__all__, f"acf.science.dynamics.__all__ missing {name!r}"
        assert hasattr(dynamics_pkg, name)

    convection_pkg = importlib.import_module("acf.science.convection")
    assert "SevereWeather" in convection_pkg.__all__
    assert hasattr(convection_pkg, "SevereWeather")

    thermodynamics_pkg = importlib.import_module("acf.science.thermodynamics")
    assert "Moisture" in thermodynamics_pkg.__all__
    assert hasattr(thermodynamics_pkg, "Moisture")


def test_internal_cross_references_use_the_new_packages_directly():
    """synoptic.py depends on potential_vorticity.py (§4c) and
    moisture.py depends on 7 same-package thermodynamics siblings
    (§4a) - locks in both resolve directly within their own package,
    not through the acf.science shim."""
    import acf.science.dynamics.synoptic as synoptic_module
    import acf.science.thermodynamics.moisture as moisture_module
    from acf.science.dynamics.potential_vorticity import PotentialVorticity
    from acf.science.thermodynamics.dewpoint import DewPoint
    from acf.science.thermodynamics.saturation_vapor_pressure import SaturationVaporPressure

    assert synoptic_module.PotentialVorticity is PotentialVorticity
    assert moisture_module.DewPoint is DewPoint
    assert moisture_module.SaturationVaporPressure is SaturationVaporPressure


def test_already_migrated_awci_dependents_reach_the_moved_modules_directly():
    """6 already-migrated awci.* modules (from earlier phases) depend
    on modules moved in this phase - locks in they were repointed to
    the new direct locations rather than left resolving through the
    acf.science shim."""
    import awci.complexity.workstation_fields as workstation_fields_module
    import awci.data.archive_field as archive_field_module
    import awci.hazards.hydrometeor_phase as hydrometeor_phase_module
    from acf.science.convection.severe_weather import SevereWeather
    from acf.science.dynamics.cyclones import BruntVaisalaFrequency
    from acf.science.precipitation.precipitation import HydrometeorType
    from acf.science.thermodynamics.moisture import Moisture

    assert hydrometeor_phase_module.HydrometeorType is HydrometeorType
    assert workstation_fields_module.BruntVaisalaFrequency is BruntVaisalaFrequency
    assert workstation_fields_module.SevereWeather is SevereWeather
    assert archive_field_module.Moisture is Moisture
