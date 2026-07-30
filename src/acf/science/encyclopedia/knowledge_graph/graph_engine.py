"""
Atmospheric Complexity Framework (ACF)

Scientific Knowledge Graph Engine
"""

from typing import Any, Dict, List, Set, Tuple


class KnowledgeGraphEngine:
    """
    Moteur de Graphe de Connaissances Scientifiques interconnectant les phénomènes atmosphériques.
    """

    def __init__(self):
        self._adj: Dict[str, Dict[str, str]] = {}
        self._reverse_adj: Dict[str, Dict[str, str]] = {}
        self._build_default_graph()

    def add_edge(self, source: str, target: str, relation: str = "leads_to"):
        """
        Ajoute une relation orientée entre deux concepts scientifiques.
        """
        src = source.lower()
        tgt = target.lower()

        if src not in self._adj:
            self._adj[src] = {}
        self._adj[src][tgt] = relation

        if tgt not in self._reverse_adj:
            self._reverse_adj[tgt] = {}
        self._reverse_adj[tgt][src] = relation

    def get_related_concepts(self, concept: str) -> List[Tuple[str, str]]:
        """
        Retourne la liste des concepts directement reliés à un concept donné.
        """
        c = concept.lower()
        res = []
        if c in self._adj:
            for tgt, rel in self._adj[c].items():
                res.append((tgt, rel))
        if c in self._reverse_adj:
            for src, rel in self._reverse_adj[c].items():
                if (src, rel) not in res:
                    res.append((src, rel))
        return res

    def find_path(self, source: str, target: str) -> List[str]:
        """
        Trouve le chemin le plus court (BFS) entre deux concepts scientifiques.
        """
        src = source.lower()
        tgt = target.lower()

        if src == tgt:
            return [src]

        queue = [[src]]
        visited: Set[str] = {src}

        while queue:
            path = queue.pop(0)
            node = path[-1]

            for neighbor in self._adj.get(node, {}):
                if neighbor == tgt:
                    return path + [neighbor]
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(path + [neighbor])

        return []

    def explain_chain(self, source: str, target: str) -> Dict[str, Any]:
        """
        Génère l'explication physique pas-à-pas de la chaîne causale reliant deux phénomènes.
        """
        path = self.find_path(source, target)
        if not path:
            return {
                "source": source,
                "target": target,
                "connected": False,
                "chain": [],
                "explanation": f"Aucun lien direct ou indirect identifié entre '{source}' et '{target}'.",
            }

        steps = []
        for i in range(len(path) - 1):
            src_node = path[i]
            tgt_node = path[i + 1]
            relation = self._adj.get(src_node, {}).get(tgt_node, "relié à")
            steps.append(f"{src_node.upper()} --[{relation}]--> {tgt_node.upper()}")

        return {
            "source": source,
            "target": target,
            "connected": True,
            "path": path,
            "chain": steps,
            "explanation": " -> ".join([p.upper() for p in path]),
        }

    def _build_default_graph(self):
        """
        Construit le graphe canonique par défaut des connexions physiques atmosphériques.
        """
        # Convection & severe weather chain
        self.add_edge("cape", "convective_instability", "causes")
        self.add_edge("convective_instability", "updraft", "generates")
        self.add_edge("updraft", "cumulus", "forms")
        self.add_edge("cumulus", "cumulonimbus", "develops_into")
        self.add_edge("cumulonimbus", "lightning", "produces")
        self.add_edge("cumulonimbus", "hail", "produces")
        self.add_edge("cumulonimbus", "heavy_rain", "produces")
        self.add_edge("cumulonimbus", "supercell", "can_organize_into")

        # Thermodynamics -> Clouds
        self.add_edge("temperature", "density", "determines")
        self.add_edge("pressure", "density", "determines")
        self.add_edge("humidity", "saturation", "leads_to")
        self.add_edge("saturation", "condensation", "triggers")
        self.add_edge("condensation", "cloud_water", "produces")
        self.add_edge("cloud_water", "rain", "converts_to_via_autoconversion")

        # Dynamics -> Vorticity
        self.add_edge("wind_shear", "vorticity", "generates")
        self.add_edge("vorticity", "ertel_pv", "contributes_to")
        self.add_edge("ertel_pv", "tropopause_fold", "diagnoses")

        # Radiation -> Surface
        self.add_edge("solar_radiation", "surface_heating", "drives")
        self.add_edge("surface_heating", "sensible_heat_flux", "generates")
        self.add_edge("surface_heating", "latent_heat_flux", "evaporates_water")
        self.add_edge("latent_heat_flux", "humidity", "increases")
