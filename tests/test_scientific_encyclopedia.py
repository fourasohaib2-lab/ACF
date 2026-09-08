"""
Tests for ACF-020+ Atmospheric Scientific Encyclopedia Engine
"""

import pytest

from acf.science import EncyclopediaEntry, EncyclopediaRegistry, KnowledgeGraphEngine, ScientificRegistry


def test_encyclopedia_registry_load_and_lookup():
    entry = EncyclopediaRegistry.get("ideal_gas_law")
    assert entry is not None
    assert isinstance(entry, EncyclopediaEntry)
    assert entry.name == "Équation d'État du Gaz Parfait"
    assert entry.latex_equation == r"p = \rho R_d T"
    assert "Pa" in entry.units.values()
    assert len(entry.references) > 0
    assert len(entry.application_conditions) > 0


def test_encyclopedia_calculation():
    val = EncyclopediaRegistry.calculate("ideal_gas_law", density=1.2, temperature=300.0)
    assert pytest.approx(val, rel=1e-3) == 103340.88


def test_encyclopedia_search():
    results = EncyclopediaRegistry.search("Boussinesq")
    assert len(results) > 0
    # CORRECTED: search() iterates a dict in insertion (import) order, so
    # asserting a specific *first* result among several equally-matching
    # entries was itself accidentally import-order-dependent (the same
    # fragility class as the "ideal_gas_law" key-collision bug fixed
    # alongside this) - there are now two independent, correctly-named
    # Boussinesq entries (dynamics.py's density-perturbation form and
    # atmosphere.py's momentum-equation form) and either may legitimately
    # come first. Assert membership instead of a fragile ordering.
    result_keys = {r.key for r in results}
    assert "boussinesq_approximation" in result_keys
    assert "boussinesq_approximation_momentum_form" in result_keys


def test_encyclopedia_domains():
    domains = EncyclopediaRegistry.domains()
    assert "Physique Atmosphérique" in domains
    assert "Thermodynamique Atmosphérique" in domains
    assert "Nuages & Microphysique" in domains


def test_scientific_registry_synchronization():
    law = ScientificRegistry.get("ideal_gas_law")
    assert law is not None
    assert law.name == "Équation d'État du Gaz Parfait"


def test_knowledge_graph_path_finding():
    graph = KnowledgeGraphEngine()
    path = graph.find_path("cape", "lightning")
    assert len(path) > 0
    assert path[0] == "cape"
    assert path[-1] == "lightning"
    assert "cumulonimbus" in path


def test_knowledge_graph_explanation_chain():
    graph = KnowledgeGraphEngine()
    explanation = graph.explain_chain("cape", "cumulonimbus")
    assert explanation["connected"] is True
    assert len(explanation["chain"]) >= 3
    assert "CAPE" in explanation["explanation"]
