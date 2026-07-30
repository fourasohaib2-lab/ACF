"""
Tests for ACF-019 Scientific Knowledge Engine Foundation
"""

import pytest
from acf.science import ScientificRegistry, AtmosphericLaw


def test_scientific_registry_get():
    law = ScientificRegistry.get("hydrostatic_equilibrium")
    assert law is not None
    assert isinstance(law, AtmosphericLaw)
    assert law.name == "Équilibre Hydrostatique"
    assert "dp/dz = -rho * g" in law.equation
    assert "Pa" in law.units.values()
    assert len(law.references) > 0
    assert len(law.limitations) > 0


def test_scientific_registry_calculation():
    law = ScientificRegistry.get("hydrostatic_equilibrium")
    dp = law.calculate(density=1.225, gravity=9.81, dz=10.0)
    assert pytest.approx(dp, rel=1e-3) == -120.1725


def test_ideal_gas_law_calculation():
    law = ScientificRegistry.get("ideal_gas_law")
    p = law.calculate(density=1.2, temperature=300.0)
    assert pytest.approx(p, rel=1e-3) == 103340.88


def test_virtual_temperature_calculation():
    law = ScientificRegistry.get("virtual_temperature")
    tv = law.calculate(temperature=300.0, specific_humidity=0.01)
    assert pytest.approx(tv, rel=1e-3) == 301.824


def test_stefan_boltzmann_calculation():
    law = ScientificRegistry.get("stefan_boltzmann")
    e = law.calculate(temperature=300.0)
    assert pytest.approx(e, rel=1e-3) == 459.300


def test_isa_temperature_calculation():
    law = ScientificRegistry.get("isa_temperature_profile")
    t_1000m = law.calculate(altitude_m=1000.0)
    assert pytest.approx(t_1000m, rel=1e-3) == 281.65


def test_scientific_registry_domains():
    domains = ScientificRegistry.domains()
    assert "Physique Atmosphérique" in domains
    assert "Thermodynamique" in domains
    assert "Dynamique Atmosphérique" in domains
    assert "Couche Limite Atmosphérique" in domains
    assert "Microphysique des Nuages" in domains
    assert "Rayonnement Atmosphérique" in domains
    assert "Aéronautique" in domains
    assert "Mathématiques Appliquées" in domains


def test_scientific_registry_search():
    results = ScientificRegistry.search("Clausius-Clapeyron")
    assert len(results) > 0
    assert results[0].key == "clausius_clapeyron"


def test_scientific_registry_count():
    assert ScientificRegistry.count() >= 25
