"""
Atmospheric Complexity Framework (ACF)

Global Autonomous Earth Operating System (AEOS) Platform Test Suite (MISSION ACF-038)
"""

import os

from acf.aeos.aeos_kernel import AEOSKernel
from acf.aeos.agents.autonomous_agents import AgentManager
from acf.aeos.distributed.cluster_manager import ClusterManager
from acf.aeos.events.event_bus import PlanetaryEvent, PlanetaryEventBus
from acf.aeos.health.self_healing import SelfHealingEngine
from acf.aeos.knowledge.knowledge_evolution import KnowledgeEvolutionEngine
from acf.aeos.orchestration.model_orchestrator import ModelConsensus, ModelExecutionPlan, ModelOrchestrator
from acf.aeos.reports.aeos_report import AEOSReportGenerator
from acf.aeos.resources.resource_optimizer import ResourceOptimizer
from acf.aeos.scheduler.task_scheduler import AEOSTask, TaskScheduler
from acf.aeos.services.service_registry import ServiceRegistry
from acf.aeos.visualization.mission_control import MissionControlDashboard
from acf.aeos.workflow.workflow_engine import WorkflowEngine
from acf.science.query_engine import ScientificQueryEngine


def test_aeos_kernel_lifecycle():
    """Test du cycle de vie du noyau AEOS (boot, shutdown, restart, health_check)."""
    kernel = AEOSKernel()
    boot_res = kernel.boot()
    assert boot_res["status"] == "BOOTED / OPERATIONAL"
    assert len(kernel.active_services) == 15

    health = kernel.health_check()
    assert health["kernel_status"] == "HEALTHY"

    shutdown_res = kernel.shutdown()
    assert shutdown_res["status"] == "SHUTDOWN COMPLETE"


def test_service_registry():
    """Test du registre des 15 microservices scientifiques d'AEOS."""
    services = ServiceRegistry.list_registered_services()
    assert len(services) == 15
    assert "AtmosphereService" in services
    assert "DigitalTwinService" in services

    info = ServiceRegistry.get_service_info("SpaceWeatherService")
    assert info is not None
    assert info["domain"] == "SpaceWeather"


def test_task_scheduler_and_workflows():
    """Test du planificateur de tâches autonomes et du moteur de workflows."""
    scheduler = TaskScheduler()
    scheduler.submit_task(AEOSTask("T1", "Data Ingestion Task", priority=1))
    scheduler.submit_task(AEOSTask("T2", "AI Inference Task", priority=2))

    res = scheduler.execute_pending_tasks()
    assert res["tasks_executed_count"] == 2

    workflows = WorkflowEngine.get_registered_workflows()
    assert len(workflows) >= 4
    assert workflows[0].name == "Global 10-Day Coupled Neural Forecast"


def test_cluster_manager_distributed_computing():
    """Test du gestionnaire de cluster distribué (Slurm, Kubernetes, MPI)."""
    cluster = ClusterManager.get_cluster_status(backend="Slurm")
    assert cluster["active_backend"] == "Slurm"
    assert cluster["total_nodes"] == 64
    assert cluster["active_workers"] == 256


def test_self_healing_and_knowledge_evolution():
    """Test de l'auto-guérison du système et de l'évolution du graphe de connaissances."""
    # CORRECTED: run_system_health_audit()/update_knowledge_graph()
    # used to unconditionally claim "100% HEALTHY" / "100% VERIFIED
    # SCIENTIFIC ACCURACY" with no real scan/validation behind either.
    health_audit = SelfHealingEngine.run_system_health_audit()
    assert health_audit["system_integrity_status"] == "NOT_AUDITED_NO_REAL_SCAN_PERFORMED"
    assert health_audit["is_real_data"] is False

    ke = KnowledgeEvolutionEngine.update_knowledge_graph()
    assert "v38.0" in ke["current_schema_version"]
    assert ke["consistency_check"] == "NOT_VERIFIED_NO_LITERATURE_MONITORING_PIPELINE"


def test_model_orchestration_and_resource_optimization():
    """Test de l'orchestration des modèles (IFS, AROME, GraphCast) et de l'optimiseur de ressources."""
    plan = ModelOrchestrator.create_execution_plan("GraphCast")
    assert isinstance(plan, ModelExecutionPlan)
    assert plan.grid_resolution_km == 25.0

    consensus = ModelOrchestrator.evaluate_model_consensus("2m_temperature")
    assert isinstance(consensus, ModelConsensus)
    assert consensus.ensemble_spread < 0.5

    # CORRECTED: optimize_resources() used to return fixed fake
    # numbers (48.0 GB GPU, 128 threads, 10.0 Gbps) regardless of the
    # real machine. cpu_threads_active is now a real os.cpu_count()
    # reading; GPU/network are honestly None (no library to query them).
    resources = ResourceOptimizer.optimize_resources()
    assert resources["gpu_memory_allocated_gb"] is None
    assert resources["cpu_threads_active"] == os.cpu_count()
    assert resources["is_real_data"] is True


def test_planetary_event_bus_and_autonomous_agents():
    """Test du bus d'événements pub/sub et du réseau de 10 agents scientifiques autonomes."""
    bus = PlanetaryEventBus()
    received = []

    def callback(evt: PlanetaryEvent):
        received.append(evt.event_id)

    bus.subscribe("CycloneDetected", callback)
    published_count = bus.publish(
        PlanetaryEvent("EVT-01", "CycloneDetected", {"name": "Typhoon"}, "2026-08-02T08:00:00Z")
    )
    assert published_count == 1
    assert len(received) == 1

    agent_mgr = AgentManager()
    assert len(agent_mgr.list_agents()) == 10
    agent_res = agent_mgr.run_all_agents()
    assert agent_res["active_agents_count"] == 10


def test_mission_control_dashboard_and_reporting():
    """Test du tableau de bord AEOS Mission Control et de la génération de rapports."""
    meta = MissionControlDashboard.get_dashboard_metadata()
    assert meta["workspace_name"] == "AEOS MISSION CONTROL CENTER"

    # CORRECTED: used to unconditionally embed fabricated figures
    # ("100% HEALTHY", "15/15 microservices", "93.8% Model Consensus",
    # "14.5% CPU / 22.0% RAM" - the exact same fake CPU/RAM pair
    # independently found in AEOSKernel.health_check(), fixed earlier
    # this session) regardless of report_type or any real system
    # state - no AEOSKernel instance is connected here.
    report = AEOSReportGenerator.generate_report("Operational")
    assert report["format"] == "Markdown"
    assert "Autonomous Earth Operating System" in report["content"]
    assert "93.8%" not in report["content"]
    assert report["is_real_data"] is False


def test_query_engine_aeos_queries():
    """Test des requêtes du ScientificQueryEngine pour le système AEOS."""
    q_engine = ScientificQueryEngine()

    r1 = q_engine.ask("Show AEOS")
    assert r1["workspace_name"] == "AEOS MISSION CONTROL CENTER"

    r2 = q_engine.ask("Show Services")
    assert r2["widget_type"] == "AEOSWorkflowSchedulerViewer"
    # active_services: 15 is a verified real number (matches
    # AEOSKernel.active_services after boot(), confirmed above) - kept
    # as-is, unlike health_status below.
    assert r2["active_services"] == 15

    # CORRECTED: used to claim a fixed "health_status: 100% HEALTHY"
    # with no connection at all to AEOSKernel.health_check() (which
    # genuinely checks self.is_booted) - this router never even
    # instantiates a kernel.
    r3 = q_engine.ask("Show Health")
    assert r3["health_status"] is None
