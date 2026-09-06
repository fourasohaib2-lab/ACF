"""
Atmospheric Complexity Framework (ACF)

Global Autonomous Earth Operating System (AEOS) & Self-Evolving Platform (MISSION ACF-038)

AUDIT NOTE (2026-09-06, Tier E sweep): a real, self-consistent
micro-kernel simulation (AEOSKernel.boot()/shutdown()/restart() manage
real internal state; PlanetaryEventBus is a genuine, if synchronous,
pub/sub implementation; 11 of 13 files already carry their own real
fix disclosures - fabricated cluster/telemetry/consensus/workflow
status already removed by earlier passes) - but, verified by grep,
AEOSKernel and every class re-exported below is not constructed
anywhere in src/ outside this package's own tests/test_aeos_platform.py.
Unlike acf.model4d (Tier F, reclassified Tier X for exactly this
reason), acf.aeos is Tier E - "desired for v1.0, not individually
release-blocking" already accounts for a module like this one; no
reclassification needed, just disclosed here since nothing else in
this package's own files states it package-wide.
"""

from acf.aeos.aeos_kernel import AEOSKernel
from acf.aeos.agents.autonomous_agents import AgentManager
from acf.aeos.distributed.cluster_manager import ClusterManager
from acf.aeos.events.event_bus import PlanetaryEventBus
from acf.aeos.health.self_healing import SelfHealingEngine
from acf.aeos.knowledge.knowledge_evolution import KnowledgeEvolutionEngine
from acf.aeos.orchestration.model_orchestrator import ModelConsensus, ModelExecutionPlan, ModelOrchestrator
from acf.aeos.reports.aeos_report import AEOSReportGenerator
from acf.aeos.resources.resource_optimizer import ResourceOptimizer
from acf.aeos.scheduler.task_scheduler import TaskScheduler
from acf.aeos.services.service_registry import ServiceRegistry
from acf.aeos.visualization.mission_control import MissionControlDashboard
from acf.aeos.workflow.workflow_engine import ScientificWorkflow, WorkflowEngine

__all__ = [
    "AEOSKernel",
    "AEOSReportGenerator",
    "AgentManager",
    "ClusterManager",
    "KnowledgeEvolutionEngine",
    "MissionControlDashboard",
    "ModelConsensus",
    "ModelExecutionPlan",
    "ModelOrchestrator",
    "PlanetaryEventBus",
    "ResourceOptimizer",
    "ScientificWorkflow",
    "SelfHealingEngine",
    "ServiceRegistry",
    "TaskScheduler",
    "WorkflowEngine",
]
