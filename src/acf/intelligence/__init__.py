"""
Atmospheric Complexity Framework (ACF)

Global Earth Intelligence & Autonomous Scientific Reasoning Platform (MISSION ACF-037)
"""

from acf.intelligence.agents.manager import ScientificAgentManager
from acf.intelligence.anomalies.anomaly_engine import EarthAnomalyEngine
from acf.intelligence.decision_support.decision_engine import DecisionSupportEngine, RecommendedAction
from acf.intelligence.explanations.physics_explainer import ScientificExplanationEngine
from acf.intelligence.forecast_analysis.forecast_reasoning import ForecastReasoningEngine
from acf.intelligence.hypothesis.hypothesis_engine import HypothesisEngine, PhysicalHypothesis
from acf.intelligence.knowledge.knowledge_updater import KnowledgeEvolutionEngine
from acf.intelligence.optimization.evacuation import EmergencyOptimizationEngine
from acf.intelligence.planner.mission_planner import MissionPlanner
from acf.intelligence.reports.executive_report import AutonomousReportGenerator
from acf.intelligence.scientific_reasoning import ScientificReasoningEngine, ScientificReasoningReport
from acf.intelligence.visualization.intelligence_dashboard import EarthIntelligenceDashboard

__all__ = [
    "AutonomousReportGenerator",
    "DecisionSupportEngine",
    "EarthAnomalyEngine",
    "EarthIntelligenceDashboard",
    "EmergencyOptimizationEngine",
    "ForecastReasoningEngine",
    "HypothesisEngine",
    "KnowledgeEvolutionEngine",
    "MissionPlanner",
    "PhysicalHypothesis",
    "RecommendedAction",
    "ScientificAgentManager",
    "ScientificExplanationEngine",
    "ScientificReasoningEngine",
    "ScientificReasoningReport",
]
