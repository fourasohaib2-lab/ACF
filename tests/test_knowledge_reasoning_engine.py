"""
Atmospheric Complexity Framework (ACF)

Knowledge & Reasoning Engine Test Suite
"""

import pytest
import acf.science
from acf.science.encyclopedia.knowledge_graph.nodes import KnowledgeNode
from acf.science.encyclopedia.knowledge_graph.relations import KnowledgeRelation
from acf.science.encyclopedia.knowledge_graph.graph_engine import KnowledgeGraphEngine
from acf.science.encyclopedia.knowledge_graph.reasoning import KnowledgeReasoningEngine
from acf.science.query_engine import ScientificQueryEngine, ask


def test_knowledge_node_structure():
    """Test la structure et la sérialisation des KnowledgeNode."""
    node = KnowledgeNode(
        key="cape",
        name="Convective Available Potential Energy",
        domain="Thermodynamique",
        description="Énergie disponible pour l'ascendance",
        equation="CAPE = int g*(Tv-Tve)/Tve dz",
        variables={"CAPE": "J/kg"},
        units={"CAPE": "J/kg"},
        references=["WMO Severe Weather Guide"],
    )
    assert node.key == "cape"
    assert node.domain == "Thermodynamique"
    d = node.to_dict()
    assert d["key"] == "cape"
    assert "references" in d


def test_knowledge_relation_structure():
    """Test la structure et la sérialisation des KnowledgeRelation."""
    rel = KnowledgeRelation(
        source="cape",
        target="instabilité",
        relation_type="engendre",
        cause="Super-adiabatisme vertical",
        equation="CAPE > 1000",
        domain="Thermodynamique",
        reference="NOAA SPC",
    )
    assert rel.source == "cape"
    assert rel.target == "instabilité"
    d = rel.to_dict()
    assert d["relation_type"] == "engendre"


def test_knowledge_graph_engine_operations():
    """Test les opérations d'enregistrement et de recherche sur KnowledgeGraphEngine."""
    graph = KnowledgeGraphEngine()
    node = KnowledgeNode("test_concept", "Test Concept", "Domaine Test")
    graph.add_node(node)
    assert graph.get_node("test_concept") is not None

    rel = KnowledgeRelation("test_concept", "grêle", "leads_to", "Cause test")
    graph.add_relation(rel)

    path = graph.find_path("test_concept", "grêle")
    assert path == ["test_concept", "grêle"]

    chain = graph.explain_chain("cumulonimbus", "grêle")
    assert chain["connected"] is True
    assert len(chain["chain"]) >= 1


def test_knowledge_reasoning_engine():
    """Test le moteur de raisonnement physique automatisé."""
    reasoner = KnowledgeReasoningEngine()
    conv = reasoner.analyze_convective_chain()
    assert conv["connected"] is True
    assert "explanation" in conv


def test_scientific_query_engine_orage_hail():
    """Test la réponse à la question 'Pourquoi un orage produit de la grêle ?'."""
    engine = ScientificQueryEngine()
    res = engine.ask("Pourquoi un orage produit de la grêle ?")

    assert "physical_explanation" in res
    assert "causal_chain" in res
    assert "equations" in res
    assert "parameters" in res
    assert "references" in res

    assert len(res["equations"]) >= 1
    assert len(res["references"]) >= 1
    assert "CAPE" in res["parameters"]

    # Global shortcut test
    res_global = ask("Pourquoi un orage produit de la grêle ?")
    assert res_global["physical_explanation"] == res["physical_explanation"]
