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

    # CORRECTED (2026-09-05 audit de continuation): monitor_services()
    # used to unconditionally claim "RUNNING / HEALTHY" for every
    # active service with no real liveness probe behind it.
    statuses = kernel.monitor_services()
    assert len(statuses) == 15
    assert all(v == "NOT_MONITORED_NO_HEALTH_PROBE_CONNECTED" for v in statuses.values())

    # CORRECTED: scheduler()/event_loop()/resource_manager() used to
    # unconditionally claim "Active"/"Processing Events"/"Allocating
    # Memory and Threads" - none of them create or run anything real.
    assert "NOT_CONNECTED_NO_SCHEDULER_INSTANCE_RUNNING" in kernel.scheduler()
    assert "NOT_RUNNING_NO_EVENT_LOOP_STARTED" in kernel.event_loop()
    assert "NOT_CONNECTED_NO_REAL_ALLOCATION_LOGIC" in kernel.resource_manager()

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

    # CORRECTED: execute_pending_tasks() used to unconditionally mark
    # every task "COMPLETED" and claim "WORKFLOW EXECUTION SUCCESS" -
    # AEOSTask carries no executable payload and no task runner exists,
    # so nothing was ever actually executed.
    res = scheduler.execute_pending_tasks()
    assert res["tasks_executed_count"] == 2
    assert res["status"] == "NOT_EXECUTED_NO_TASK_RUNNER_CONNECTED"

    # CORRECTED: workflow status used to claim a fabricated
    # per-instance runtime state ("COMPLETED"/"ACTIVE"/"STANDBY") for
    # a static catalog - no real orchestration run/tracking exists.
    workflows = WorkflowEngine.get_registered_workflows()
    assert len(workflows) >= 4
    assert workflows[0].name == "Global 10-Day Coupled Neural Forecast"
    assert workflows[0].status == "NOT_TRACKED_NO_ORCHESTRATION_RUN"


def test_cluster_manager_distributed_computing():
    """Test du gestionnaire de cluster distribué (Slurm, Kubernetes, MPI)."""
    # CORRECTED: used to unconditionally claim a fixed "64" total_nodes
    # / "256" active_workers regardless of backend, with 0 real cluster
    # connection.
    cluster = ClusterManager.get_cluster_status(backend="Slurm")
    assert cluster["active_backend"] == "Slurm"
    assert cluster["total_nodes"] is None
    assert cluster["active_workers"] is None
    assert cluster["is_real_data"] is False


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
    # CORRECTED: used to return the identical fixed
    # (25.0km, 37 levels, 240h, 4 nodes) for ANY of the 9 supported
    # models - IFS/AROME/ICON/GraphCast have genuinely different real
    # resolutions, and no real per-model deployment-planning capability
    # exists yet.
    plan = ModelOrchestrator.create_execution_plan("GraphCast")
    assert isinstance(plan, ModelExecutionPlan)
    assert plan.model_name == "GraphCast"
    assert plan.grid_resolution_km is None
    assert plan.is_real_data is False

    # CORRECTED: used to unconditionally claim a fixed
    # ensemble_mean=18.4/ensemble_spread=0.35/"HIGH CONSENSUS" with 0
    # real outputs ever gathered from any of the 9 orchestrated models.
    consensus = ModelOrchestrator.evaluate_model_consensus("2m_temperature")
    assert isinstance(consensus, ModelConsensus)
    assert consensus.ensemble_spread is None
    assert consensus.consensus_level == "NOT_COMPUTED_NO_MODEL_OUTPUTS_CONNECTED"
    assert consensus.is_real_data is False

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

    # CORRECTED (2026-09-05 audit de continuation): observe()/reason()/
    # act() used to return a plain narrative sentence ("Observing
    # domain...", "Reasoning on physical laws...", "Executing
    # autonomous action...") with no real data read, rule applied, or
    # action executed behind any of the three - same fabrication
    # pattern as acf.model4d's *_engine.py, disclosed the same way.
    cycle = agent_res["agent_cycles"]["MeteorologyAgent"]
    assert "NOT_REAL_OBSERVATION_NO_DATA_SOURCE_CONNECTED" in cycle["observe"]
    assert "NOT_REAL_REASONING_NO_RULE_ENGINE_CONNECTED" in cycle["reason"]
    assert "NOT_REAL_ACTION_NOTHING_EXECUTED" in cycle["act"]


def test_mission_control_dashboard_and_reporting():
    """Test du tableau de bord AEOS Mission Control et de la génération de rapports."""
    # CORRECTED: system_telemetry used to claim a fixed "14.5% CPU /
    # 22.0% RAM" - the exact same fake pair independently found in
    # AEOSKernel.health_check() and AEOSReportGenerator, both fixed
    # earlier this session - and "32 active_gpu_nodes", with no real
    # system query performed.
    meta = MissionControlDashboard.get_dashboard_metadata()
    assert meta["workspace_name"] == "AEOS MISSION CONTROL CENTER"
    assert meta["system_telemetry"]["cpu_usage_pct"] is None

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
