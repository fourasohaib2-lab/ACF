"""
Atmospheric Complexity Framework (ACF)

Planetary Knowledge Graph & Inter-Domain Scientific Knowledge Base Module (Phase 6)
(PlanetaryKnowledgeGraph linking Atmosphere, Ocean, Hydrology, Climate, Cryosphere, Space Weather, Geology)
"""

from typing import Any, Dict, List


class PlanetaryKnowledgeGraph:
    """
    Graphe de connaissances planétaire unifié reliant tous les domaines scientifiques d'ACF.
    """

    @classmethod
    def get_domain_nodes(cls) -> List[str]:
        return [
            "Atmosphere",
            "Ocean",
            "Hydrology",
            "Climate",
            "Cryosphere",
            "Geology",
            "Space Weather",
            "Aviation Safety",
            "Artificial Intelligence",
            "Observatories & Satellites",
        ]

    @classmethod
    def explain_planetary_link(cls, source_domain: str, target_domain: str) -> Dict[str, Any]:
        """Explique la relation causale physique entre deux sous-systèmes du Digital Twin."""
        s = source_domain.lower()
        t = target_domain.lower()

        if "atmosphere" in s and "ocean" in t:
            explanation = "Atmospheric wind stress drives ocean surface currents (Ekman Transport) and sea-state wave growth (WAVEWATCH III)."
        elif "space" in s and "atmosphere" in t:
            explanation = "Solar X-ray flares ionize the D-layer causing HF radio blackouts, while geomagnetic storms trigger Joule heating in the thermosphere."
        elif "geology" in s and "ocean" in t:
            explanation = "Subduction megathrust earthquakes displace the seafloor, generating open-ocean tsunami waves propagating at c = sqrt(g*d)."
        else:
            explanation = f"Physical inter-system feedback loop coupling {source_domain} and {target_domain} in the ACF Earth Digital Twin."

        return {
            "source_domain": source_domain,
            "target_domain": target_domain,
            "physical_coupling_explanation": explanation,
        }
