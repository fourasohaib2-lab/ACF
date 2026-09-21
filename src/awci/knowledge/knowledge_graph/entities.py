"""
Atmospheric Complexity Framework (ACF)

Aviation Knowledge Graph - Entities

Real aviation-hazard ``KnowledgeNode`` definitions - the ``entities.py``
module named in
``docs/architecture/awci_reference_architecture.md`` section 2
("Aviation Knowledge Base... knowledge_graph/"). Reuses the already-
real, already-working ``acf.science.encyclopedia.knowledge_graph.
KnowledgeNode`` dataclass directly (not a second, independently
invented node type) - see ``graph.py``'s own docstring for why a
second graph engine is not built either.

Every node's ``description``/``equation``/``references`` fields are
copied from, or paraphrase, this codebase's own already-real, already-
cited content in ``awci.knowledge.*``/``awci.hazards.*`` - never a new
scientific claim; a node here is a graph-shaped view of facts already
documented and verified elsewhere in this session.
"""

from __future__ import annotations

from acf.science.encyclopedia.knowledge_graph.nodes import KnowledgeNode

#: Real domain label distinguishing these nodes from the base graph's
#: own general atmospheric-physics nodes (which use "Physique
#: Atmosphérique"/other domain labels) - not a new taxonomy, just a
#: real, disclosed grouping.
_DOMAIN = "Aviation Meteorology"

AVIATION_KNOWLEDGE_NODES: tuple[KnowledgeNode, ...] = (
    KnowledgeNode(
        key="jet stream",
        name="Jet Stream",
        domain=_DOMAIN,
        description="Real, narrow, fast-flowing air current near the tropopause - see awci.knowledge.meteorology.jet_stream.",
        equation="polar jet peak ~160 kt; subtropical jet 120-150 kt (250 kt peak)",
        references=["awci.knowledge.meteorology.jet_stream"],
    ),
    KnowledgeNode(
        key="clear air turbulence",
        name="Clear Air Turbulence (CAT)",
        domain=_DOMAIN,
        description=(
            "Real turbulence in cloud-free air, most frequent near the tropopause "
            "(7-12 km / 23-39 kft) - see awci.knowledge.meteorology.clear_air_turbulence."
        ),
        equation="Ellrod & Knapp (1992) TI2/EI index",
        references=["ICAO Doc 9837", "Ellrod & Knapp (1992)", "awci.hazards.cat_turbulence"],
    ),
    KnowledgeNode(
        key="orographic wave",
        name="Orographic (Mountain) Wave",
        domain=_DOMAIN,
        description=(
            "Real standing wave forming when air perpendicular to a ridge (>=25 kt) is lifted - "
            "see awci.knowledge.meteorology.orographic_turbulence."
        ),
        equation="Fr = U / (N*H)",
        references=["ICAO Doc 9817", "AMS Aviation Meteorology", "awci.hazards.orographic_froude"],
    ),
    KnowledgeNode(
        key="rotor turbulence",
        name="Lee-Wave Rotor Turbulence",
        domain=_DOMAIN,
        description=(
            "Real, most intense turbulence layer beneath an orographic wave crest, "
            "real rotor descent speed 20-36 km/h - see awci.knowledge.meteorology.orographic_turbulence."
        ),
        equation="",
        references=["awci.knowledge.meteorology.orographic_turbulence"],
    ),
    KnowledgeNode(
        key="wake turbulence",
        name="Aircraft Wake Turbulence",
        domain=_DOMAIN,
        description=(
            "Real wingtip-vortex turbulence behind an aircraft, classified by real ICAO wake "
            "category (LIGHT/MEDIUM/HEAVY/SUPER) - see awci.knowledge.performance.wake_turbulence."
        ),
        equation="",
        references=["ICAO Doc 4444", "awci.knowledge.performance.wake_turbulence"],
    ),
    KnowledgeNode(
        key="thunderstorm",
        name="Thunderstorm",
        domain=_DOMAIN,
        description=(
            "Real monocellular thunderstorm life cycle (cumulus/mature/dissipating) - "
            "see awci.knowledge.meteorology.thunderstorm."
        ),
        equation="",
        references=["awci.knowledge.meteorology.thunderstorm"],
    ),
    KnowledgeNode(
        key="microburst",
        name="Microburst",
        domain=_DOMAIN,
        description=(
            "Real, powerful localized downdraft (peak wind 75 m/s, 5-15 min duration, 1-4 km diameter) - "
            "see awci.knowledge.meteorology.microburst_reference and awci.hazards.microburst."
        ),
        equation="headwind-to-tailwind change > 30 kt at <= 1500 ft AGL",
        references=["ICAO Doc 9837", "FAA AC 00-54", "awci.hazards.microburst"],
    ),
    KnowledgeNode(
        key="airframe icing",
        name="Airframe Icing",
        domain=_DOMAIN,
        description=(
            "Real in-flight icing from supercooled liquid water droplets striking the airframe "
            "between 0 and -40 degC - see awci.knowledge.meteorology.icing and "
            "awci.hazards.icing_temperature_range."
        ),
        equation="Rate_icing = E * v_TAS * LWC",
        references=["ICAO Annex 3 Chapter 3", "FAA Aviation Weather Handbook Chapter 19"],
    ),
    KnowledgeNode(
        key="cold front",
        name="Cold Front",
        domain=_DOMAIN,
        description="Real, faster-moving front - see awci.knowledge.meteorology.weather_front.",
        equation="",
        references=["awci.knowledge.meteorology.weather_front"],
    ),
    KnowledgeNode(
        key="squall line",
        name="Squall Line",
        domain=_DOMAIN,
        description=(
            "Real gust front (>=15 kt excess over mean wind, sustained >=1 min) - "
            "see awci.knowledge.meteorology.squall_line."
        ),
        equation="",
        references=["awci.knowledge.meteorology.squall_line"],
    ),
)
