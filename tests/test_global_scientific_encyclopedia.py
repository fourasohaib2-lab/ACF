"""
Tests for MISSION ACF-022 Global Atmospheric Scientific Knowledge Expansion Engine
"""

import pytest
import acf.science as acf_science
from acf.science import EncyclopediaRegistry, KnowledgeGraphEngine, ScientificQueryEngine, ask


def test_global_encyclopedia_total_entries():
    count = EncyclopediaRegistry.count()
    assert count >= 40


def test_clausius_clapeyron_calculation():
    es = EncyclopediaRegistry.calculate("clausius_clapeyron_equation", temp_k=298.15)
    assert es > 3000.0  # ~3167 Pa at 25°C


def test_aerodynamic_lift_calculation():
    lift = EncyclopediaRegistry.calculate("aerodynamic_lift_force", density=1.225, velocity=100.0, surface_area=30.0, Cz=0.5)
    assert lift == 0.5 * 1.225 * 10000.0 * 30.0 * 0.5


def test_nwp_database_ukmo_model():
    entry = EncyclopediaRegistry.get("nwp_ukmo_unified_model")
    assert entry is not None
    assert "Unified Model" in entry.name


def test_enhanced_knowledge_graph_metadata():
    graph = KnowledgeGraphEngine()
    chain = graph.explain_chain("cape", "foudre")
    assert chain["connected"] is True
    assert len(chain["detailed_edges"]) > 0
    first_edge = chain["detailed_edges"][0]
    assert "cause" in first_edge
    assert "equation" in first_edge
    assert "reference" in first_edge


def test_scientific_query_engine_ask():
    answer = ask("Pourquoi un cumulonimbus produit de la grêle ?")
    assert "cumulonimbus" in answer["question"].lower()
    assert len(answer["physical_explanation"]) > 0
    assert len(answer["equations"]) > 0
    assert len(answer["references"]) > 0
    assert len(answer["causal_chain"]) > 0


def test_scientific_query_engine_class():
    engine = ScientificQueryEngine()
    res = engine.ask("Pourquoi la foudre apparait sous les orages ?")
    assert "foudre" in res["question"].lower()
    assert "CAPE" in res["parameters"]
