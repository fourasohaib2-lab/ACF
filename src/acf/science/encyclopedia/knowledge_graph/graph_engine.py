"""
Atmospheric Complexity Framework (ACF)

Professional Scientific Knowledge Graph Engine
"""

from typing import Any, Dict, List, Optional, Set, Tuple
from acf.science.encyclopedia.knowledge_graph.nodes import KnowledgeNode
from acf.science.encyclopedia.knowledge_graph.relations import KnowledgeRelation


class KnowledgeGraphEngine:
    """
    Moteur de Graphe de Connaissances Scientifiques interconnectant les phénomènes atmosphériques.
    """

    def __init__(self):
        self._nodes: Dict[str, KnowledgeNode] = {}
        self._relations: List[KnowledgeRelation] = []
        self._adj: Dict[str, Dict[str, KnowledgeRelation]] = {}
        self._reverse_adj: Dict[str, Dict[str, KnowledgeRelation]] = {}
        self._build_default_graph()

    def add_node(self, node: KnowledgeNode):
        """
        Ajoute un nœud conceptuel structuré au graphe.
        """
        key = node.key.lower()
        self._nodes[key] = node

    def add_relation(self, relation: KnowledgeRelation):
        """
        Ajoute une relation causale structurée orientée entre deux nœuds.
        """
        src = relation.source.lower()
        tgt = relation.target.lower()

        self._relations.append(relation)

        if src not in self._adj:
            self._adj[src] = {}
        self._adj[src][tgt] = relation

        if tgt not in self._reverse_adj:
            self._reverse_adj[tgt] = {}
        self._reverse_adj[tgt][src] = relation

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
        Ajoute une relation orientée entre deux concepts (compatibilité ascendante).
        """
        rel_obj = KnowledgeRelation(
            source=source,
            target=target,
            relation_type=relation,
            cause=cause,
            equation=equation,
            domain=domain,
            reference=reference,
        )
        self.add_relation(rel_obj)

    def get_node(self, key: str) -> Optional[KnowledgeNode]:
        """
        Récupère un nœud par sa clé.
        """
        return self._nodes.get(key.lower())

    def get_related_concepts(self, concept: str) -> List[Tuple[str, str]]:
        """
        Retourne la liste des concepts directement reliés à un concept donné.
        """
        c = concept.lower()
        res = []
        if c in self._adj:
            for tgt, rel in self._adj[c].items():
                res.append((tgt, rel.relation_type))
        if c in self._reverse_adj:
            for src, rel in self._reverse_adj[c].items():
                if (src, rel.relation_type) not in res:
                    res.append((src, rel.relation_type))
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
            rel_obj = self._adj.get(src_node, {}).get(tgt_node)
            rel_type = rel_obj.relation_type if rel_obj else "relié à"
            eq = rel_obj.equation if rel_obj else ""
            cause = rel_obj.cause if rel_obj else ""
            dom = rel_obj.domain if rel_obj else ""
            ref = rel_obj.reference if rel_obj else ""

            steps.append(f"{src_node.upper()} --[{rel_type}]--> {tgt_node.upper()}")
            detailed_edges.append({
                "source": src_node,
                "target": tgt_node,
                "relation": rel_type,
                "cause": cause,
                "equation": eq,
                "domain": dom,
                "reference": ref,
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
        # Register core physical nodes
        nodes_data = [
            KnowledgeNode("surface heating", "Chauffage de Surface par Rayonnement Solaire", "Rayonnement & Surface", "Réchauffement diurne de la couche limite", "F_sensible = rho * c_p * C_H * U10 * (T_sfc - T_air)", variables={"F_sensible": "W/m²"}, units={"F_sensible": "W/m²"}, references=["Stull (1988)"]),
            KnowledgeNode("chauffage au sol", "Chauffage diurne du sol", "Thermodynamique", "Chauffage par rayonnement court", "Q_sens = H", variables={"H": "W/m²"}, units={"H": "W/m²"}, references=["Stull (1988)"]),
            KnowledgeNode("cape", "Énergie Potentielle Convective Disponible (CAPE)", "Thermodynamique", "Énergie disponible pour l'ascendance", "CAPE = int g*(Tv-Tve)/Tve dz", variables={"CAPE": "J/kg"}, units={"CAPE": "J/kg"}, references=["WMO Severe Weather Guide"]),
            KnowledgeNode("instabilité", "Instabilité Atmosphérique", "Thermodynamique", "État d'équilibre instable de la masse d'air", "dT/dz > Gamma_m", variables={"Lapse_rate": "K/km"}, units={"Lapse_rate": "K/km"}, references=["NOAA SPC"]),
            KnowledgeNode("instability", "Atmospheric Instability", "Thermodynamics", "Unstable lapse rate", "dT/dz > Gamma_m", variables={"Lapse_rate": "K/km"}, units={"Lapse_rate": "K/km"}, references=["NOAA SPC"]),
            KnowledgeNode("ascendance", "Ascendance Convective (Updraft)", "Dynamique Convective", "Courant d'air ascendant rapide", "w_max = sqrt(2*CAPE)", variables={"w_max": "m/s"}, units={"w_max": "m/s"}, references=["Holton & Hakim (2012)"]),
            KnowledgeNode("updraft", "Convective Updraft", "Convective Dynamics", "Upward vertical velocity", "w_max = sqrt(2*CAPE)", variables={"w_max": "m/s"}, units={"w_max": "m/s"}, references=["Holton & Hakim (2012)"]),
            KnowledgeNode("cumulonimbus", "Cumulonimbus (Cb)", "Microphysique Nuageuse", "Nuage d'orage à grand développement vertical", "z_top > 10 km", variables={"H_top": "km"}, units={"H_top": "km"}, references=["WMO International Cloud Atlas"]),
            KnowledgeNode("collision glace-graupel", "Collision Cristaux de Glace et Graupels", "Électricité Atmosphérique", "Électrification non-inductive dans la zone de phase mixte", "Delta_q = f(T, LWC)", variables={"Delta_q": "pC"}, units={"Delta_q": "pC"}, references=["Takahashi (1978)"]),
            KnowledgeNode("électricité", "Électrification et Charge Séparation", "Électricité Atmosphérique", "Accumulation de charges électriques opposées", "E > 3 kV/cm", variables={"E": "V/m"}, units={"E": "V/m"}, references=["Rakov & Uman (2003)"]),
            KnowledgeNode("foudre", "Foudre et Éclairs", "Physique des Plasmas", "Décharge électrique violente nuage-sol ou intra-nuage", "I_peak > 30 kA", variables={"I_peak": "kA"}, units={"I_peak": "kA"}, references=["Price & Rind (1992)"]),
            KnowledgeNode("lightning", "Lightning & Thunderstorms", "Atmospheric Electricity", "Electric breakdown of air", "E > 3e5 V/m", variables={"E": "V/m"}, units={"E": "V/m"}, references=["Rakov & Uman (2003)"]),
            KnowledgeNode("fortes précipitations", "Fortes Précipitations (Pluie Convective)", "Hydrométéorologie", "Précipitations intenses sous la cellule convective", "Z = 200 * R^1.6", variables={"R": "mm/h"}, units={"R": "mm/h"}, references=["Marshall & Palmer (1948)"]),
            KnowledgeNode("heavy rain", "Heavy Convective Rainfall", "Hydrometeorology", "Intense precipitation rate", "Z = 200 * R^1.6", variables={"R": "mm/h"}, units={"R": "mm/h"}, references=["Marshall & Palmer (1948)"]),
            KnowledgeNode("grêle", "Grêle (Hail)", "Phénomènes Violents", "Chute de grêlons formés par givrage humide", "MESH = 2.54 * SHI^0.5", variables={"Diameter": "mm"}, units={"Diameter": "mm"}, references=["Knight & Knight (2001)"]),
            KnowledgeNode("hail", "Hailstones", "Severe Weather", "Supercooled accretion on graupel", "MESH = 2.54 * SHI^0.5", variables={"Diameter": "mm"}, units={"Diameter": "mm"}, references=["Knight & Knight (2001)"]),
            KnowledgeNode("crue éclair", "Crue Éclair (Flash Flood)", "Hydrologie & Risques", "Submersion rapide du bassin versant", "Q_p = (C * I * A) / 3.6", variables={"Qp": "m³/s"}, units={"Qp": "m³/s"}, references=["WMO Flash Flood Guidance System System"]),
            KnowledgeNode("flash flood", "Flash Flood Hazard", "Hydrology", "Rapid watershed inundation", "Q_p = (C * I * A) / 3.6", variables={"Qp": "m³/s"}, units={"Qp": "m³/s"}, references=["WMO FFGS"]),
        ]
        for n in nodes_data:
            self.add_node(n)

        # Convective & Flash Flood Causal Chain (cape -> instabilité -> ascendance -> cumulonimbus)
        self.add_edge("surface heating", "instability", relation="causes", cause="Diurnal radiative flux warming the boundary layer", equation="F_sensible = rho*cp*CH*U10*(Tsfc-Tair)", domain="Boundary Layer", reference="Stull (1988)")
        self.add_edge("chauffage au sol", "instabilité", relation="engendre", cause="Chauffage diurne réchauffant la couche de surface", equation="dT/dt = -1/rho/cp * dF/dz", domain="Thermodynamique", reference="Stull (1988)")
        self.add_edge("surface heating", "cape", relation="increases", cause="Increase in surface equivalent potential temperature", equation="CAPE = int g*(Tv-Tve)/Tve dz", domain="Thermodynamics", reference="NOAA SPC")
        self.add_edge("instability", "cape", relation="manifests as", cause="Unstable lapse rate", equation="CAPE = int g*(Tv-Tve)/Tve dz", domain="Thermodynamics", reference="NOAA SPC")
        self.add_edge("cape", "instabilité", relation="engendre", cause="Forte énergie convective disponible", equation="CAPE = int g*(Tv-Tve)/Tve dz", domain="Thermodynamique", reference="WMO Severe Weather Guide")
        self.add_edge("instabilité", "ascendance", relation="génère", cause="Poussée d'Archimède positive accélérant la parcelle d'air", equation="w_max = sqrt(2*CAPE)", domain="Dynamique Convective", reference="Holton & Hakim (2012)")
        self.add_edge("instability", "updraft", relation="generates", cause="Positive buoyancy force", equation="w_max = sqrt(2*CAPE)", domain="Convective Dynamics", reference="Holton & Hakim (2012)")
        self.add_edge("ascendance", "cumulonimbus", relation="développe", cause="Condensation continue et soulèvement au-dessus du LFC", equation="z_LCL = 125*(T-Td)", domain="Microphysique Nuageuse", reference="WMO International Cloud Atlas")
        self.add_edge("updraft", "cumulonimbus", relation="builds", cause="Continuous condensation above LFC", equation="z_LCL = 125*(T-Td)", domain="Cloud Physics", reference="WMO International Cloud Atlas")
        self.add_edge("cumulonimbus", "collision glace-graupel", relation="déclenche", cause="Brassage intense et coexistence de phase mixte", equation="S_ice = e_i < e_w", domain="Microphysique des Nuages", reference="Pruppacher & Klett (1997)")
        self.add_edge("collision glace-graupel", "électricité", relation="induit", cause="Transfert de charge non-inductif entre cristaux de glace et graupels", equation="Delta_q = f(T, LWC)", domain="Électricité Atmosphérique", reference="Takahashi (1978)")
        self.add_edge("électricité", "foudre", relation="produit", cause="Claquage diélectrique de l'air quand E > 3 kV/cm", equation="E_breakdown = 3e5 V/m", domain="Physique des Plasmas Atmosphériques", reference="Rakov & Uman (2003)")
        self.add_edge("électricité", "lightning", relation="produit", cause="Dielectric breakdown of air", equation="E_breakdown = 3e5 V/m", domain="Atmospheric Electricity", reference="Rakov & Uman (2003)")
        self.add_edge("cumulonimbus", "lightning", relation="produit", cause="Séparation de charges non-inductive en zone de phase mixte", equation="F_flash = 3.44e-5 * H_top^4.9", domain="Électricité Atmosphérique", reference="Price & Rind (1992)")
        self.add_edge("cumulonimbus", "foudre", relation="produit", cause="Séparation de charges non-inductive en zone de phase mixte", equation="F_flash = 3.44e-5 * H_top^4.9", domain="Électricité Atmosphérique", reference="Price & Rind (1992)")
        self.add_edge("cumulonimbus", "heavy rain", relation="produit", cause="Massive autoconversion and accretion of cloud water", equation="Z = 200 * R^1.6", domain="Radar & Hydrometeorology", reference="Marshall & Palmer (1948)")
        self.add_edge("cumulonimbus", "fortes précipitations", relation="produit", cause="Autoconversion et accrétion massive d'eau nuageuse", equation="Z = 200 * R^1.6", domain="Radar & Précipitations", reference="Marshall & Palmer (1948)")
        self.add_edge("cumulonimbus", "grêle", relation="produit", cause="Givrage humide répété des graupels dans le courant ascendant", equation="Diameter = 0.05 * w_max", domain="Précipitations Violentes", reference="Knight & Knight (2001)")
        self.add_edge("cumulonimbus", "hail", relation="produit", cause="Wet growth accretion of supercooled droplets on graupel", equation="Diameter = 0.05 * w_max", domain="Severe Weather", reference="Knight & Knight (2001)")
        self.add_edge("lightning", "heavy rain", relation="accompanies", cause="Updraft collapse and precipitating hydrometeor fallout", equation="Z = 200 * R^1.6", domain="Hydrometeorology", reference="Marshall & Palmer (1948)")
        self.add_edge("foudre", "fortes précipitations", relation="accompagne", cause="Effondrement du courant ascendant et déversement d'hydrométéores", equation="Z = 200 * R^1.6", domain="Hydrométéorologie", reference="Marshall & Palmer (1948)")
        self.add_edge("heavy rain", "flash flood", relation="causes", cause="Rainfall intensity exceeding soil infiltration capacity", equation="Q_p = (C * I * A) / 3.6", domain="Hydrology", reference="WMO Flash Flood Guidance System")
        self.add_edge("fortes précipitations", "crue éclair", relation="provoque", cause="Intensité de précipitation supérieure à la capacité d'infiltration du sol", equation="Q_p = (C * I * A) / 3.6", domain="Hydrologie", reference="WMO FFGS")
