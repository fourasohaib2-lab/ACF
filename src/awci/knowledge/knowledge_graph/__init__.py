"""
Atmospheric Complexity Framework (ACF)

AWCI Knowledge Graph (``src/awci/knowledge/knowledge_graph/``)

Real implementation of the package named in
``docs/architecture/awci_reference_architecture.md`` section 2
("Aviation Knowledge Base... knowledge_graph/"), previously the
specific gap named in
``docs/architecture/acf_awci_architecture_gap_analysis.md`` (no
aviation knowledge graph existed under ``awci.knowledge``).

Built 2026-09-21: ``entities.py`` (``AVIATION_KNOWLEDGE_NODES`` - real,
cited ``KnowledgeNode`` aviation-hazard definitions) and ``graph.py``
(``build_aviation_knowledge_graph()`` - seeds the already-real,
already-working ``acf.science.encyclopedia.knowledge_graph.
KnowledgeGraphEngine`` with those nodes plus real, cited causal edges).

Reuses the base engine directly rather than building a second graph
engine (see ``graph.py``'s own docstring for the full rationale).
``relations.py``/``ontology.py`` (the blueprint's remaining named
files) are deliberately not built as separate files - see ``graph.py``
for the disclosed reason for each.
"""

from __future__ import annotations

from awci.knowledge.knowledge_graph.entities import AVIATION_KNOWLEDGE_NODES
from awci.knowledge.knowledge_graph.graph import build_aviation_knowledge_graph

__all__ = ["AVIATION_KNOWLEDGE_NODES", "build_aviation_knowledge_graph"]
