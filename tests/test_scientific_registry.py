"""
Tests for acf.science.registry.ScientificRegistry, focused on the laws
registered alongside the CAPE/CIN physical fix and the canonical
Bolton (1980) equivalent potential temperature.
"""

from acf.science.registry import ScientificRegistry


def test_cape_law_registered_and_computes():
    law = ScientificRegistry.get("cape_buoyancy_integral")
    assert law is not None
    value = law.calculate(
        parcel_temperature=[22, 18, 14],
        environment_temperature=[20, 16, 13],
        height=[0, 1000, 2000],
    )
    assert value > 0


def test_cin_law_registered_and_computes():
    law = ScientificRegistry.get("cin_buoyancy_integral")
    assert law is not None
    value = law.calculate(
        parcel_temperature=[18, 15, 10],
        environment_temperature=[20, 17, 12],
        height=[0, 1000, 2000],
    )
    assert value > 0


def test_bolton_equivalent_potential_temperature_law_registered():
    law = ScientificRegistry.get("equivalent_potential_temperature_bolton_1980")
    assert law is not None
    value = law.calculate(temperature_k=300.0, dewpoint_k=290.0, pressure_hpa=1000.0)
    assert value > 300.0


def test_thermodynamics_domain_lists_new_laws():
    keys = {law.key for law in ScientificRegistry.list_laws(domain="Thermodynamique")}
    assert {"cape_buoyancy_integral", "cin_buoyancy_integral", "equivalent_potential_temperature_bolton_1980"} <= keys
