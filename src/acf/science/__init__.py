"""
Atmospheric Complexity Framework (ACF)

SCIENCE Subsystem, Scientific Knowledge Engine, Parameter Engine, Scientific Encyclopedia & Query Engine

AUDIT NOTE (2026-09-06, Tier F sweep - see ARCHITECTURE.md §3 /
docs/STATUS.md): unlike acf.model4d (reclassified to Tier X the same
day - see model4d's own docstring), this package is real, load-bearing
infrastructure actually used throughout ACF (e.g. acf.science.divergence.
Divergence is the divergence implementation the shipped codebase calls,
per acf.model4d's own docstring's own comparison).

Verification performed: repo-wide grep for the generic templated-
docstring bloat pattern found in other packages before their audits
(0 hits in encyclopedia/, 6 hits among the 152 top-level files - all 6
are trivial 1-3-method unit-conversion classes (Pressure/DewPoint/
Humidity/Wind/Temperature/engine.py) where the actual code, visible
directly below the boilerplate header, is self-evidently correct - not
rewritten, lower priority than packages where the bloat text was the
file's only content); grep for stub/fake/placeholder markers across
all 152 top-level files (6 hits, all already-honest disclosures of
genuine, cited gaps - e.g. fronts.py/synoptic.py's Thermal Front
Parameter, surface_fire.py's Canadian FWI System - not problems) and
across encyclopedia/'s 60 files (1 hit, already an honest disclosure);
registry.py, engine.py, and query_engine.py (1739 lines, already
carrying 16 "CORRECTED"-tagged fixes from earlier sessions' systematic
sequential reads) read in full; encyclopedia/knowledge_graph/
graph_engine.py (566 lines) read in full and confirmed to be a
genuine graph implementation (real adjacency lists, BFS shortest-path,
causal-chain explanation) - unlike model4d's same-named engine, this
one is not a name/implementation mismatch; physics_ai/ read in full
and found to honestly label itself as architecture specifications
("Spécifications et formulations"), not a claim of running PINN/FNO/
GraphCast models.

854 tests passed (every test file importing acf.science). Not an
individual line-by-line read of all 152 top-level + 60 encyclopedia/
files - see docs/STATUS.md for the precise methodology this claim
rests on.
"""

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.knowledge_graph.graph_engine import KnowledgeGraphEngine
from acf.science.encyclopedia.registry import EncyclopediaRegistry
from acf.science.laws.base_law import AtmosphericLaw, ScientificLaw
from acf.science.parameters.engine import ParameterEngine
from acf.science.parameters.physical_parameter import PhysicalParameter
from acf.science.query_engine import ScientificQueryEngine, ask
from acf.science.registry import ScientificRegistry

__all__ = [
    "AtmosphericLaw",
    "EncyclopediaEntry",
    "EncyclopediaRegistry",
    "KnowledgeGraphEngine",
    "ParameterEngine",
    "PhysicalParameter",
    "ScientificLaw",
    "ScientificQueryEngine",
    "ScientificRegistry",
    "ask",
]
