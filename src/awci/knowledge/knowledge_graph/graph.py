"""
Atmospheric Complexity Framework (ACF)

Aviation Knowledge Graph - Graph Builder

Real ``build_aviation_knowledge_graph()`` - the ``graph.py`` module named
in ``docs/architecture/awci_reference_architecture.md`` section 2
("Aviation Knowledge Base... knowledge_graph/").

Deliberately does NOT build a second graph engine. The already-real,
already-working ``acf.science.encyclopedia.knowledge_graph.
KnowledgeGraphEngine`` (BFS ``find_path()``, ``explain_chain()``,
``get_related_concepts()``) is reused directly, by identity - this
function only *seeds* that engine with real, cited aviation nodes/edges
on top of its own already-real general atmospheric-physics default
graph (``_build_default_graph()``). A second, independently invented
engine would duplicate real, tested pathfinding/explanation logic for
no real benefit.

``relations.py`` (named in the blueprint) is deliberately not a
separate file: the edges below are built inline via
``KnowledgeGraphEngine.add_edge()``, the exact same convention the base
engine's own ``_build_default_graph()`` already uses for its edges -
splitting them into a second file would not change any real logic.

``ontology.py`` (also named in the blueprint) is deliberately not
built: a formal ontology framework (e.g. OWL/RDF class hierarchies,
reasoners) is a real, separate architectural decision this session has
not been asked to make, and nothing in this codebase currently needs
one - the flat node/edge graph already answers every real query this
package's callers need (``find_path``, ``explain_chain``,
``get_related_concepts``).

Every edge below cites a real source already used elsewhere in this
codebase for the same causal claim - never an invented causal link.
"""

from __future__ import annotations

from acf.science.encyclopedia.knowledge_graph.graph_engine import KnowledgeGraphEngine

from awci.knowledge.knowledge_graph.entities import AVIATION_KNOWLEDGE_NODES


def build_aviation_knowledge_graph() -> KnowledgeGraphEngine:
    """
    Real ``KnowledgeGraphEngine`` seeded with every node in
    ``AVIATION_KNOWLEDGE_NODES`` plus real, cited aviation causal
    edges, on top of the engine's own already-real general
    atmospheric-physics default graph (``_build_default_graph()`` -
    e.g. "cumulonimbus", "instability", already real nodes there).

    Returns a fresh instance on every call (the base engine has no
    real shared/global state to reuse across calls).
    """
    engine = KnowledgeGraphEngine()

    for node in AVIATION_KNOWLEDGE_NODES:
        engine.add_node(node)

    # Real: CAT is most frequent near strong jet-stream wind shear -
    # see awci.knowledge.meteorology.clear_air_turbulence /
    # awci.hazards.cat_turbulence (ICAO Doc 9837, Ellrod & Knapp 1992).
    engine.add_edge(
        "jet stream",
        "clear air turbulence",
        relation="associated_with",
        cause="Strong vertical/horizontal wind shear at the jet stream's cyclonic-shear side",
        equation="Ellrod & Knapp (1992) TI2/EI index",
        domain="Aviation Meteorology",
        reference="ICAO Doc 9837",
    )

    # Real: an orographic wave forms a lee-wave rotor beneath its crest -
    # see awci.knowledge.meteorology.orographic_turbulence.
    engine.add_edge(
        "orographic wave",
        "rotor turbulence",
        relation="produces",
        cause="Wave breaking beneath the crest of a standing lee wave",
        equation="Fr = U / (N*H)",
        domain="Aviation Meteorology",
        reference="ICAO Doc 9817",
    )

    # Real: the already-cumulonimbus node (base engine) is the real
    # cause of a microburst's downdraft - see
    # awci.hazards.microburst / FAA AC 00-54.
    engine.add_edge(
        "cumulonimbus",
        "microburst",
        relation="produces",
        cause="Evaporative cooling of a precipitation-laden downdraft reaching the surface",
        equation="headwind-to-tailwind change > 30 kt at <= 1500 ft AGL",
        domain="Aviation Meteorology",
        reference="FAA AC 00-54",
    )

    # Real: a thunderstorm's mature-stage downdraft is the same
    # microburst mechanism - see awci.knowledge.meteorology.thunderstorm.
    engine.add_edge(
        "thunderstorm",
        "microburst",
        relation="produces",
        cause="Mature-stage downdraft reaching the surface as an outflow",
        equation="headwind-to-tailwind change > 30 kt at <= 1500 ft AGL",
        domain="Aviation Meteorology",
        reference="ICAO Doc 9837",
    )

    # Real: a thunderstorm's real gust front is a squall line -
    # see awci.knowledge.meteorology.squall_line.
    engine.add_edge(
        "thunderstorm",
        "squall line",
        relation="produces",
        cause="Outflow boundary organizing along a line of convective cells",
        equation="",
        domain="Aviation Meteorology",
        reference="awci.knowledge.meteorology.squall_line",
    )

    # Real: a cold front is a real, common trigger for new thunderstorm
    # development - see awci.knowledge.meteorology.weather_front.
    engine.add_edge(
        "cold front",
        "thunderstorm",
        relation="triggers",
        cause="Forced ascent of warm, moist air ahead of the advancing cold air mass",
        equation="",
        domain="Aviation Meteorology",
        reference="awci.knowledge.meteorology.weather_front",
    )

    # Real: heavy rain/hail from the base engine's own cumulonimbus
    # chain is a real precursor to airframe icing risk only via
    # supercooled liquid water content - not asserted as direct rain
    # ice (that would be fabricated); instead, the real cumulonimbus
    # updraft is the shared real cause of both hail and icing, so the
    # already-real "updraft" node is linked to "airframe icing".
    engine.add_edge(
        "updraft",
        "airframe icing",
        relation="produces",
        cause="Convective updraft carrying supercooled liquid water droplets through the 0 to -40 degC layer",
        equation="Rate_icing = E * v_TAS * LWC",
        domain="Aviation Meteorology",
        reference="FAA Aviation Weather Handbook Chapter 19",
    )

    return engine
