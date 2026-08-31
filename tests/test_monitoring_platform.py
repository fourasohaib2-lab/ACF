"""
Atmospheric Complexity Framework (ACF)

Global Real-Time Earth Monitoring Platform Test Suite (MISSION ACF-044)
"""

from acf.monitoring.alert_dispatcher import OperationalAlertDispatcher
from acf.monitoring.anomaly_monitor import EarthAnomalyMonitor
from acf.monitoring.earth_health import EarthHealthMonitor
from acf.monitoring.event_stream import PlanetaryEventStream
from acf.monitoring.monitoring_dashboard import AWCIMonitoringDashboard
from acf.monitoring.monitoring_registry import MonitoringRegistry
from acf.monitoring.observation_stream import ObservationStreamEngine
from acf.monitoring.realtime_monitor import GlobalRealtimeMonitor
from acf.monitoring.telemetry_engine import TelemetryEngine
from acf.monitoring.websocket_server import OperationalWebSocketServer
from acf.science.query_engine import ScientificQueryEngine


def test_global_realtime_monitor():
    """Test du moniteur principal en temps réel et de la synchronisation."""
    # CORRECTED: start_monitoring_loop()/sync_earth_state() used to
    # claim "RUNNING"/"100% OPERATIONAL" with a fabricated synced-
    # sources list - no real loop or Digital Twin sync actually runs.
    mon = GlobalRealtimeMonitor()
    start_res = mon.start_monitoring_loop()
    assert start_res["status"] == "FLAG_SET_NO_REAL_LOOP_STARTED"
    assert mon.is_active is True

    sync_res = mon.sync_earth_state()
    assert sync_res["sync_health"] == "NOT_SYNCHRONIZED_NO_DATA_SOURCE_CONNECTED"
    assert sync_res["data_sources_synced"] == []

    stop_res = mon.stop_monitoring_loop()
    assert stop_res["status"] == "STOPPED"


def test_telemetry_engine():
    """Test du moteur de télémétrie matérielle et de la grappe HPC."""
    # CORRECTED: collect_telemetry() used to unconditionally claim a
    # full fabricated hardware battery (14.2% CPU, 32.5% GPU, 16
    # cluster nodes...). Now reports real host CPU/RAM via psutil and
    # honestly declines metrics with no real probe (GPU, cluster,
    # AEOS, network, FPS).
    telem = TelemetryEngine.collect_telemetry()
    assert telem["cpu_usage_pct"] is not None
    assert telem["cpu_usage_pct"] >= 0
    assert telem["gpu_usage_pct"] is None
    assert telem["cluster_nodes_active"] is None
    assert telem["system_status"] == "HOST_CPU_RAM_ONLY_OTHER_METRICS_NOT_CONNECTED"


def test_observation_stream_engine():
    """Test du moteur de streaming d'observations (satellites, radars, bouées)."""
    # CORRECTED: the satellite/radar catalogs are genuine, but this
    # used to also claim fabricated live throughput numbers ("4500
    # stations/sec"...) and "REALTIME_STREAMING_NOMINAL" - no real
    # ingestion pipeline is connected.
    obs = ObservationStreamEngine.get_stream_telemetry()
    assert len(obs["supported_satellites"]) >= 5
    assert len(obs["supported_radar_products"]) >= 4
    assert obs["surface_stations_ingested_per_sec"] is None
    assert obs["stream_ingestion_status"] == "NOT_STREAMING_NO_INGESTION_PIPELINE_CONNECTED"


def test_websocket_server_and_event_stream():
    """Test du serveur WebSocket et du bus d'événements planétaires à priorité."""
    # CORRECTED: start_server()/broadcast_event() used to claim
    # "LISTENING"/"DISPATCHED" with no real socket ever bound and no
    # real client connection handling.
    ws = OperationalWebSocketServer(port=8088)
    assert ws.start_server()["status"] == "FLAG_SET_NO_REAL_SOCKET_BOUND"

    bcast = ws.broadcast_event("CycloneDetected", {"cyclone_id": "AL052026"})
    assert bcast["broadcast_status"] == "NOT_DISPATCHED_NO_REAL_SERVER_CONNECTED"
    assert ws.stop_server()["status"] == "STOPPED"

    # PlanetaryEventStream is a genuine pub/sub implementation - unchanged.
    bus = PlanetaryEventStream()
    pub = bus.publish("CycloneDetected", {"name": "Category 4 Storm"}, priority="HIGH")
    assert pub["status"] == "PUBLISHED"
    assert pub["event"]["event_type"] == "CycloneDetected"


def test_anomaly_alert_health_and_registry():
    """Test du déctecteur d'anomalies, du régulateur d'alertes, du score de santé et du registre."""
    # CORRECTED: scan_for_anomalies() used to unconditionally claim a
    # specific fabricated anomaly and "NOMINAL / LOW ANOMALY" - no
    # real observation data connected.
    anom = EarthAnomalyMonitor.scan_for_anomalies()
    assert anom["anomaly_level"] == "NOT_SCANNED_NO_OBSERVATION_DATA_CONNECTED"
    assert anom["physical_anomalies"] == []

    # CORRECTED: dispatch_alert() genuinely validates level/echoes
    # inputs, but used to claim "SENT_AND_ACKNOWLEDGED" with no real
    # channel integration - same issue as CommunicationEngine.
    alert = OperationalAlertDispatcher.dispatch_alert("Coastal Surge Warning", "RED", ["AWCI", "EmergencyCenter"])
    assert alert["alert_level"] == "RED"
    assert alert["dispatch_status"] == "NOT_DISPATCHED_NO_CHANNEL_INTEGRATION_CONFIGURED"

    # CORRECTED: compute_earth_health_index() used to claim a
    # fabricated "74.5%" score and "6 transgressed boundaries" - no
    # real Earth-system data connected.
    health = EarthHealthMonitor.compute_earth_health_index()
    assert health["planet_health_score_pct"] is None
    assert health["overall_operational_status"] == "NOT_MONITORED_NO_DATA_SOURCE"

    # CORRECTED: the MONITORED_SERVICES catalog is genuine, but this
    # used to also claim a fabricated "18500 sensors"/"12 agents" and
    # "ALL_REGISTERED_SERVICES_HEALTHY" with no real health probe.
    reg = MonitoringRegistry.get_registry_status()
    assert reg["monitored_services_count"] >= 5
    assert reg["monitored_sensors_count"] is None
    assert reg["registry_health"] == "NOT_CHECKED_NO_HEALTH_PROBE_CONNECTED"


def test_monitoring_dashboard_and_query_engine():
    """Test des métadonnées du tableau de bord et des requêtes du QueryEngine."""
    dash = AWCIMonitoringDashboard.get_dashboard_metadata()
    assert dash["workspace_name"] == "GLOBAL REAL-TIME EARTH MONITORING MISSION CONTROL"
    assert len(dash["live_map_layers"]) >= 20
    assert "BLACK" in dash["alert_levels"]

    qe = ScientificQueryEngine()

    r1 = qe.ask("Show Live Earth")
    assert r1["workspace_name"] == "GLOBAL REAL-TIME EARTH MONITORING MISSION CONTROL"

    r2 = qe.ask("Show Telemetry")
    assert r2["widget_type"] == "TelemetryEngineViewer"

    # CORRECTED: used to claim a fixed fake "74.5" - the same
    # fabricated number independently claimed by EarthHealthMonitor
    # and PlanetaryDashboard (both fixed earlier this session). This
    # router only activates a UI widget, it doesn't measure anything.
    r3 = qe.ask("Show Earth Health")
    assert r3["planet_health_score_pct"] is None
    assert r3["widget_type"] == "EarthHealthViewer"

    # CORRECTED: used to claim a fixed "active_alert_level: ORANGE /
    # RED" as if reporting a real current alert state.
    r4 = qe.ask("Show Alerts")
    assert r4["widget_type"] == "OperationalAlertDispatcherViewer"
    assert r4["active_alert_level"] is None

    r5 = qe.ask("Show Streaming")
    assert r5["widget_type"] == "ObservationStreamEngineViewer"

    r6 = qe.ask("Show AI Monitoring")
    assert r6["widget_type"] == "AIMultiModelMonitorViewer"

    r7 = qe.ask("Explain Monitoring")
    assert len(r7["architecture_components"]) >= 5
