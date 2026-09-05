"""
Atmospheric Complexity Framework (ACF)

Autonomous Scientific Agents Module (Phase 11)
(AgentManager supervising MeteorologyAgent, OceanAgent, HydrologyAgent, ClimateAgent, CryosphereAgent, GeologyAgent, SpaceWeatherAgent, ForecastAgent, DecisionAgent, KnowledgeAgent)
"""

from typing import Any


class AutonomousAgent:
    """
    Agent scientifique autonome universel.

    NOTE (correction, 2026-09-05 audit de continuation - même famille
    que le finding de fabrication documenté dans
    acf.model4d/physics/*_engine.py): observe()/reason()/act()
    n'assemblent qu'une f-string statique avec le nom et le domaine de
    l'agent - aucune donnée n'est lue (observe), aucune règle physique
    n'est appliquée (reason) et rien n'est réellement exécuté (act).
    Non fabriqué au sens strict (aucune valeur numérique ou résultat
    n'est présenté comme mesuré/validé), mais les noms de méthode
    ("observe", "reason", "act") suggèrent une capacité d'agent IA que
    ce code ne fournit pas. Disclosure uniquement - le comportement
    (nombre d'agents, structure du cycle) reste inchangé pour ne pas
    casser le contrat de test existant (test_aeos_platform.py).
    """

    def __init__(self, name: str, domain: str):
        self.name = name
        self.domain = domain

    def observe(self) -> str:
        return f"[{self.name}] NOT_REAL_OBSERVATION_NO_DATA_SOURCE_CONNECTED (domain: {self.domain})"

    def reason(self) -> str:
        return f"[{self.name}] NOT_REAL_REASONING_NO_RULE_ENGINE_CONNECTED (domain: {self.domain})"

    def act(self) -> str:
        return f"[{self.name}] NOT_REAL_ACTION_NOTHING_EXECUTED (domain: {self.domain})"


class MeteorologyAgent(AutonomousAgent):
    def __init__(self):
        super().__init__("MeteorologyAgent", "Atmosphere & Severe Storms")


class OceanAgent(AutonomousAgent):
    def __init__(self):
        super().__init__("OceanAgent", "Oceanography & Spectral Waves")


class HydrologyAgent(AutonomousAgent):
    def __init__(self):
        super().__init__("HydrologyAgent", "River Basins & Flooding")


class ClimateAgent(AutonomousAgent):
    def __init__(self):
        super().__init__("ClimateAgent", "Earth Climate System")


class CryosphereAgent(AutonomousAgent):
    def __init__(self):
        super().__init__("CryosphereAgent", "Sea Ice & Glaciers")


class GeologyAgent(AutonomousAgent):
    def __init__(self):
        super().__init__("GeologyAgent", "Seismology & Volcanology")


class SpaceWeatherAgent(AutonomousAgent):
    def __init__(self):
        super().__init__("SpaceWeatherAgent", "Sun-Earth Environment")


class ForecastAgent(AutonomousAgent):
    def __init__(self):
        super().__init__("ForecastAgent", "Ensemble & AI Predictions")


class DecisionAgent(AutonomousAgent):
    def __init__(self):
        super().__init__("DecisionAgent", "Operational Decision Support")


class KnowledgeAgent(AutonomousAgent):
    def __init__(self):
        super().__init__("KnowledgeAgent", "Planetary Knowledge Graph")


class AgentManager:
    """
    Gestionnaire principal des 10 agents scientifiques autonomes d'AEOS.

    active_agents_count (run_all_agents()) is a genuine len(self.agents)
    count - see AutonomousAgent's own NOTE for why the per-agent
    "observe"/"reason"/"act" cycle content it aggregates is disclosed
    rather than a real observation/reasoning/action.
    """

    def __init__(self):
        self.agents = [
            MeteorologyAgent(),
            OceanAgent(),
            HydrologyAgent(),
            ClimateAgent(),
            CryosphereAgent(),
            GeologyAgent(),
            SpaceWeatherAgent(),
            ForecastAgent(),
            DecisionAgent(),
            KnowledgeAgent(),
        ]

    def list_agents(self) -> list[str]:
        return [agent.name for agent in self.agents]

    def run_all_agents(self) -> dict[str, Any]:
        results = {}
        for agent in self.agents:
            results[agent.name] = {
                "observe": agent.observe(),
                "reason": agent.reason(),
                "act": agent.act(),
            }
        return {"active_agents_count": len(self.agents), "agent_cycles": results}
