"""
Atmospheric Complexity Framework (ACF)

Enhanced Scientific Knowledge Graph Engine
"""

from typing import Any, Dict, List, Set, Tuple


class KnowledgeGraphEngine:
    """
    Moteur de Graphe de Connaissances Scientifiques interconnectant les phénomènes atmosphériques.
    """

    def __init__(self):
        self._adj: Dict[str, Dict[str, Dict[str, str]]] = {}
        self._reverse_adj: Dict[str, Dict[str, Dict[str, str]]] = {}
        self._build_default_graph()

    def add_edge(
        self,
        source: str,
        target: str,
        relation: str = "leads_to",
        cause: str = "",
        equation: str = "",
        domain: str = "Physique Atmosphérique",
        reference: str = "WMO Atmospheric Sciences Manual",
    ):
        """
        Ajoute une relation orientée enrichie entre deux concepts scientifiques.
        """
        src = source.lower()
        tgt = target.lower()

        edge_data = {
            "relation": relation,
            "cause": cause or f"{source} entraîne {target}",
            "equation": equation,
            "domain": domain,
            "reference": reference,
        }

        if src not in self._adj:
            self._adj[src] = {}
        self._adj[src][tgt] = edge_data

        if tgt not in self._reverse_adj:
            self._reverse_adj[tgt] = {}
        self._reverse_adj[tgt][src] = edge_data

    def get_related_concepts(self, concept: str) -> List[Tuple[str, str]]:
        """
        Retourne la liste des concepts directement reliés à un concept donné.
        """
        c = concept.lower()
        res = []
        if c in self._adj:
            for tgt, data in self._adj[c].items():
                res.append((tgt, data["relation"]))
        if c in self._reverse_adj:
            for src, data in self._reverse_adj[c].items():
                if (src, data["relation"]) not in res:
                    res.append((src, data["relation"]))
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
        detailed_edges = []
        for i in range(len(path) - 1):
            src_node = path[i]
            tgt_node = path[i + 1]
            data = self._adj.get(src_node, {}).get(tgt_node, {})
            rel = data.get("relation", "relié à")
            eq = data.get("equation", "")
            steps.append(f"{src_node.upper()} --[{rel}]--> {tgt_node.upper()}")
            detailed_edges.append({
                "source": src_node,
                "target": tgt_node,
                "relation": rel,
                "cause": data.get("cause", ""),
                "equation": eq,
                "domain": data.get("domain", ""),
                "reference": data.get("reference", ""),
            })

        return {
            "source": source,
            "target": target,
            "connected": True,
            "path": path,
            "chain": steps,
            "detailed_edges": detailed_edges,
            "explanation": " -> ".join([p.upper() for p in path]),
        }

    def _build_default_graph(self):
        """
        Construit le graphe canonique par défaut des connexions physiques atmosphériques.
        """
        # Convection, hail & severe weather chain
        self.add_edge("cape", "instabilité", relation="engendre", cause="Inversion de température et forte énergie convective", equation="CAPE = int g*(Tv-Tve)/Tve dz", domain="Thermodynamique", reference="WMO Severe Weather Guide")
        self.add_edge("cape", "convective_instability", relation="causes", cause="Atmospheric temperature lapse rate exceeding moist adiabat", equation="CAPE = int g*(Tv-Tve)/Tve dz", domain="Thermodynamics", reference="WMO Severe Weather Guide")
        self.add_edge("convective_instability", "updraft", relation="generates", cause="Positive buoyancy force accelerating air parcel", equation="w_max = sqrt(2*CAPE)", domain="Convective Dynamics", reference="Holton & Hakim (2012)")
        self.add_edge("instabilité", "ascendance", relation="génère", cause="Poussée d'Archimède positive accélérant la parcelle d'air", equation="w_max = sqrt(2*CAPE)", domain="Dynamique Convective", reference="Holton & Hakim (2012)")
        self.add_edge("updraft", "cumulus", relation="forms", cause="Condensation upon reaching LCL", equation="z_LCL = 125*(T-Td)", domain="Cloud Physics", reference="WMO Cloud Atlas")
        self.add_edge("ascendance", "cumulonimbus", relation="développe", cause="Condensation continue et soulèvement au-dessus du LFC", equation="z_LCL = 125*(T-Td)", domain="Microphysique Nuageuse", reference="WMO International Cloud Atlas")
        self.add_edge("cumulus", "cumulonimbus", relation="develops_into", cause="Deep moist convection breaching freezing level", equation="CAPE > 1000", domain="Cloud Physics", reference="WMO Cloud Atlas")
        self.add_edge("cumulonimbus", "collision glace-graupel", relation="déclenche", cause="Brassage intense et coexistence de phase mixte", equation="S_ice = e_i < e_w", domain="Microphysique des Nuages", reference="Pruppacher & Klett (1997)")
        self.add_edge("collision glace-graupel", "électricité", relation="induit", cause="Transfert de charge non-inductif entre cristaux de glace et graupels", equation="Delta_q = f(T, LWC)", domain="Électricité Atmosphérique", reference="Takahashi (1978)")
        self.add_edge("électricité", "foudre", relation="produit", cause="Claquage diélectrique de l'air quand E > 3 kV/cm", equation="E_breakdown = 3e5 V/m", domain="Physique des Plasmas Atmosphériques", reference="Rakov & Uman (2003)")
        self.add_edge("électricité", "lightning", relation="produit", cause="Dielectric breakdown of air", equation="E_breakdown = 3e5 V/m", domain="Atmospheric Electricity", reference="Rakov & Uman (2003)")
        self.add_edge("cumulonimbus", "lightning", relation="produces", cause="Non-inductive charge separation in mixed phase zone", equation="F_flash = 3.44e-5 * H_top^4.9", domain="Atmospheric Electricity", reference="Price & Rind (1992)")
        self.add_edge("cumulonimbus", "foudre", relation="produit", cause="Séparation de charges non-inductive en zone de phase mixte", equation="F_flash = 3.44e-5 * H_top^4.9", domain="Électricité Atmosphérique", reference="Price & Rind (1992)")
        self.add_edge("cumulonimbus", "grêle", relation="produit", cause="Givrage humide répété des graupels dans le courant ascendant", equation="Diameter = 0.05 * w_max", domain="Précipitations Violentes", reference="Knight & Knight (2001)")
        self.add_edge("cumulonimbus", "hail", relation="produces", cause="Wet growth accretion of supercooled droplets on graupel", equation="Diameter = 0.05 * w_max", domain="Severe Weather", reference="Knight & Knight (2001)")
        self.add_edge("cumulonimbus", "fortes précipitations", relation="produit", cause="Autoconversion et accrétion massive d'eau nuageuse", equation="Z = 200 * R^1.6", domain="Radar & Précipitations", reference="Marshall & Palmer (1948)")
        self.add_edge("cumulonimbus", "heavy_rain", relation="produces", cause="Massive autoconversion and accretion of cloud water", equation="Z = 200 * R^1.6", domain="Precipitation Physics", reference="Marshall & Palmer (1948)")
