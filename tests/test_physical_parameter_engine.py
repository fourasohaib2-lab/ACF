"""
Tests for ACF-020 Physical Parameter Engine
"""

import pytest

from acf.science import ParameterEngine, PhysicalParameter


def test_parameter_engine_get():
    engine = ParameterEngine()
    param = engine.get("potential_temperature")
    assert param is not None
    assert isinstance(param, PhysicalParameter)
    assert param.name == "Température Potentielle"
    assert param.symbol == "theta"
    assert param.unit == "K"
    assert "temperature" in param.dependencies
    assert "pressure" in param.dependencies


def test_parameter_engine_dependencies():
    engine = ParameterEngine()
    deps = engine.dependencies("potential_temperature")
    dep_keys = [p.key for p in deps]
    assert "temperature" in dep_keys
    assert "pressure" in dep_keys


def test_parameter_engine_dependents():
    engine = ParameterEngine()
    dependents = engine.dependents("temperature")
    dependent_keys = [p.key for p in dependents]
    assert "density" in dependent_keys
    assert "potential_temperature" in dependent_keys
    assert "speed_of_sound" in dependent_keys


def test_parameter_engine_related_laws():
    engine = ParameterEngine()
    laws = engine.related_laws("potential_temperature")
    assert len(laws) > 0
    law_keys = [law.key for law in laws]
    assert "potential_temperature" in law_keys


def test_parameter_engine_explain():
    engine = ParameterEngine()
    explanation = engine.explain("potential_temperature")
    assert explanation["parameter"] == "Température Potentielle"
    assert explanation["symbol"] == "theta"
    assert explanation["unit"] == "K"
    assert "temperature" in [d.lower() for d in explanation["direct_dependency_keys"]]
    assert len(explanation["governing_laws"]) > 0


def test_parameter_engine_dependency_tree():
    engine = ParameterEngine()
    tree = engine.dependency_tree("potential_temperature")
    assert tree["parameter"] == "potential_temperature"
    assert len(tree["dependencies"]) == 2
    dep_params = [d["parameter"] for d in tree["dependencies"]]
    assert "temperature" in dep_params
    assert "pressure" in dep_params


test_domains_coverage_data = [
    (
        "Atmosphère",
        [
            "temperature",
            "pressure",
            "density",
            "geopotential_height",
            "humidity",
            "mixing_ratio",
            "virtual_temperature",
        ],
    ),
    ("Dynamique", ["wind_u", "wind_v", "vorticity", "divergence", "potential_vorticity", "deformation"]),
    ("Thermodynamique", ["potential_temperature", "equivalent_potential_temperature", "CAPE", "CIN"]),
    ("Microphysique", ["cloud_water", "rain_water", "ice", "snow", "graupel"]),
    ("Rayonnement", ["solar_flux", "infrared_flux", "albedo"]),
    ("Aéronautique", ["mach", "reynolds", "speed_of_sound", "lift_coefficient", "drag_coefficient"]),
]


@pytest.mark.parametrize("domain_name, expected_params", test_domains_coverage_data)
def test_parameter_engine_domain_coverage(domain_name, expected_params):
    engine = ParameterEngine()
    domain_params = engine.list_parameters(domain_name)
    keys = [p.key for p in domain_params]
    for expected in expected_params:
        assert expected in keys, f"Parameter '{expected}' missing from domain '{domain_name}'"


def test_parameter_engine_register_raises_on_key_collision():
    """
    NOTE (hardening, not a fix - no collision currently exists in
    PHYSICAL_PARAMETERS, verified): mirrors the collision guard added to
    EncyclopediaRegistry.register() after that registry was found to have
    5 real silent key collisions across its many independently-imported
    modules. This registry's single source list (PHYSICAL_PARAMETERS) is
    currently collision-free, but the same "silent dict[key] = value
    overwrite with no detection" pattern existed here too.
    """
    engine = ParameterEngine()
    existing = engine.get("potential_temperature")
    assert existing is not None

    dupe = PhysicalParameter(
        key="potential_temperature",
        name="deliberately colliding test parameter",
        symbol="x",
        unit="K",
        domain="Test",
        description="d",
        physical_meaning="d",
    )
    with pytest.raises(ValueError, match="key collision"):
        engine.register(dupe)

    # The original parameter must be untouched - no partial/silent overwrite.
    assert engine.get("potential_temperature") is existing
