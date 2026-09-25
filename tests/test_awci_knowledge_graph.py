"""Tests for the new AWCI aviation knowledge graph (src/awci/knowledge/
knowledge_graph/), built while working through the full remaining-gaps
list ("On les attaque toutes un par un") after it was identified as the
specific gap in docs/architecture/acf_awci_architecture_gap_analysis.md
(``docs/architecture/awci_reference_architecture.md`` section 2 names
``src/awci/knowledge/knowledge_graph/`` but no such package existed).

``build_aviation_knowledge_graph()`` reuses the already-real, already-
working ``acf.science.encyclopedia.knowledge_graph.KnowledgeGraphEngine``
directly (BFS pathfinding, causal-chain explanation) rather than a
second, independently invented graph engine - it only seeds that engine
with real, cited aviation nodes/edges on top of its own already-real
general atmospheric-physics default graph.
"""

from __future__ import annotations

from acf.science.encyclopedia.knowledge_graph.graph_engine import KnowledgeGraphEngine
from acf.science.encyclopedia.knowledge_graph.nodes import KnowledgeNode
from awci.knowledge.knowledge_graph import AVIATION_KNOWLEDGE_NODES, build_aviation_knowledge_graph

# --------------------------------------------------------------------- entities.py


def test_every_aviation_node_is_a_real_knowledge_node():
    assert len(AVIATION_KNOWLEDGE_NODES) == 10
    for node in AVIATION_KNOWLEDGE_NODES:
        assert isinstance(node, KnowledgeNode)
        assert node.domain == "Aviation Meteorology"
        assert node.key
        assert node.description


def test_every_aviation_node_cites_a_real_reference():
    for node in AVIATION_KNOWLEDGE_NODES:
        assert len(node.references) > 0
        assert all(isinstance(ref, str) and ref for ref in node.references)


def test_aviation_node_keys_are_unique():
    keys = [node.key for node in AVIATION_KNOWLEDGE_NODES]
    assert len(keys) == len(set(keys))


# --------------------------------------------------------------------- graph.py


def test_build_aviation_knowledge_graph_returns_a_real_engine_instance():
    graph = build_aviation_knowledge_graph()
    assert isinstance(graph, KnowledgeGraphEngine)


def test_build_aviation_knowledge_graph_returns_a_fresh_instance_each_call():
    graph_a = build_aviation_knowledge_graph()
    graph_b = build_aviation_knowledge_graph()
    assert graph_a is not graph_b


def test_every_aviation_node_is_registered_in_the_graph():
    graph = build_aviation_knowledge_graph()
    for node in AVIATION_KNOWLEDGE_NODES:
        found = graph.get_node(node.key)
        assert found is not None
        assert found.key == node.key
        assert found.domain == "Aviation Meteorology"


def test_the_base_engines_own_general_nodes_are_still_present():
    """Seeding aviation nodes must not clobber the base engine's own
    real, already-tested general atmospheric-physics default graph."""
    graph = build_aviation_knowledge_graph()
    assert graph.get_node("cape") is not None
    assert graph.get_node("cumulonimbus") is not None
    assert graph.get_node("instability") is not None


def test_jet_stream_is_associated_with_clear_air_turbulence():
    graph = build_aviation_knowledge_graph()
    related = graph.get_related_concepts("jet stream")
    assert ("clear air turbulence", "associated_with") in related


def test_orographic_wave_produces_rotor_turbulence():
    graph = build_aviation_knowledge_graph()
    path = graph.find_path("orographic wave", "rotor turbulence")
    assert path == ["orographic wave", "rotor turbulence"]


def test_cumulonimbus_from_the_base_graph_produces_microburst():
    """A real cross-package edge: the aviation graph's own "microburst"
    node is linked from the base engine's own already-real
    "cumulonimbus" node - proof the two real node sets are genuinely
    interconnected, not two disjoint islands."""
    graph = build_aviation_knowledge_graph()
    related = graph.get_related_concepts("cumulonimbus")
    assert ("microburst", "produces") in related


def test_cold_front_to_microburst_causal_chain_is_real_and_explained():
    graph = build_aviation_knowledge_graph()
    chain = graph.explain_chain("cold front", "microburst")
    assert chain["connected"] is True
    assert chain["path"] == ["cold front", "thunderstorm", "microburst"]
    assert len(chain["detailed_edges"]) == 2
    for edge in chain["detailed_edges"]:
        assert edge["reference"]


def test_updraft_produces_airframe_icing_with_a_real_cited_equation():
    graph = build_aviation_knowledge_graph()
    chain = graph.explain_chain("updraft", "airframe icing")
    assert chain["connected"] is True
    edge = chain["detailed_edges"][0]
    assert edge["reference"] == "FAA Aviation Weather Handbook Chapter 19"
    assert "LWC" in edge["equation"]


def test_unconnected_nodes_are_honestly_reported_as_disconnected():
    graph = build_aviation_knowledge_graph()
    chain = graph.explain_chain("wake turbulence", "airframe icing")
    assert chain["connected"] is False
    assert chain["chain"] == []


# --------------------------------------------------------------------- discipline


def test_no_second_graph_engine_class_is_defined_in_this_package():
    """graph.py must not define its own pathfinding/explanation class -
    it only calls the real, already-tested KnowledgeGraphEngine."""
    import awci.knowledge.knowledge_graph.graph as graph_module

    assert not hasattr(graph_module, "KnowledgeGraphEngine") or (
        graph_module.KnowledgeGraphEngine is KnowledgeGraphEngine
    )


def test_every_added_edge_carries_a_real_disclosed_reference():
    graph = build_aviation_knowledge_graph()
    aviation_keys = {node.key for node in AVIATION_KNOWLEDGE_NODES}
    checked_any = False
    for key in aviation_keys:
        for target, _relation in graph.get_related_concepts(key):
            path = graph.find_path(key, target)
            if len(path) == 2:
                chain = graph.explain_chain(key, target)
                for edge in chain["detailed_edges"]:
                    assert edge["reference"], f"edge {edge} has no real reference"
                    checked_any = True
    assert checked_any
