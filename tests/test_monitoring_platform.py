"""
Atmospheric Complexity Framework (ACF)

Global Real-Time Earth Monitoring Platform Test Suite (MISSION ACF-044)
"""

from acf.monitoring.realtime_monitor import GlobalRealtimeMonitor
from acf.monitoring.telemetry_engine import TelemetryEngine
from acf.monitoring.observation_stream import ObservationStreamEngine
from acf.monitoring.websocket_server import OperationalWebSocketServer
from acf.monitoring.event_stream import PlanetaryEventStream
from acf.monitoring.anomaly_monitor import EarthAnomalyMonitor
from acf.monitoring.alert_dispatcher import OperationalAlertDispatcher
from acf.monitoring.earth_health import EarthHealthMonitor
from acf.monitoring.monitoring_registry import MonitoringRegistry
from acf.monitoring.monitoring_dashboard import AWCIMonitoringDashboard
from acf.science.query_engine import ScientificQueryEngine


def test_global_realtime_monitor():
    """Test du moniteur principal en temps réel et de la synchronisation."""
    mon = GlobalRealtimeMonitor()
    start_res = mon.start_monitoring_loop()
    assert start_res["status"] == "RUNNING"
    assert start_res["refresh_rate_hz"] == 10.0

    sync_res = mon.sync_earth_state()
    assert sync_res["sync_health"] == "100% OPERATIONAL"
    assert len(sync_res["data_sources_synced"]) >= 4

    stop_res = mon.stop_monitoring_loop()
    assert stop_res["status"] == "STOPPED"


def test_telemetry_engine():
    """Test du moteur de télémétrie matérielle et de la grappe HPC."""
    telem = TelemetryEngine.collect_telemetry()
    assert telem["cpu_usage_pct"] > 0
    assert telem["gpu_usage_pct"] > 0
    assert telem["cluster_nodes_active"] == 16
    assert telem["system_status"] == "HIGH PERFORMANCE / OPTIMAL"


def test_observation_stream_engine():
    """Test du moteur de streaming d'observations (satellites, radars, bouées)."""
    obs = ObservationStreamEngine.get_stream_telemetry()
    assert len(obs["active_satellites"]) >= 5
    assert len(obs["active_radar_products"]) >= 4
    assert obs["surface_stations_ingested_per_sec"] == 4500
    assert obs["stream_ingestion_status"] == "REALTIME_STREAMING_NOMINAL"


def test_websocket_server_and_event_stream():
    """Test du serveur WebSocket et du bus d'événements planétaires à priorité."""
    ws = OperationalWebSocketServer(port=8088)
    assert ws.start_server()["status"] == "LISTENING"

    bcast = ws.broadcast_event("CycloneDetected", {"cyclone_id": "AL052026"})
    assert bcast["broadcast_status"] == "DISPATCHED"
    assert ws.stop_server()["status"] == "STOPPED"

    bus = PlanetaryEventStream()
    pub = bus.publish("CycloneDetected", {"name": "Category 4 Storm"}, priority="HIGH")
    assert pub["status"] == "PUBLISHED"
    assert pub["event"]["event_type"] == "CycloneDetected"


def test_anomaly_alert_health_and_registry():
    """Test du déctecteur d'anomalies, du régulateur d'alertes, du score de santé et du registre."""
    anom = EarthAnomalyMonitor.scan_for_anomalies()
    assert anom["anomaly_level"] == "NOMINAL / LOW ANOMALY"

    alert = OperationalAlertDispatcher.dispatch_alert("Coastal Surge Warning", "RED", ["AWCI", "EmergencyCenter"])
    assert alert["alert_level"] == "RED"
    assert alert["dispatch_status"] == "SENT_AND_ACKNOWLEDGED"

    health = EarthHealthMonitor.compute_earth_health_index()
    assert health["planet_health_score_pct"] == 74.5
    assert health["overall_operational_status"] == "MONITORED_NOMINAL"

    reg = MonitoringRegistry.get_registry_status()
    assert reg["monitored_services_count"] >= 5
    assert reg["registry_health"] == "ALL_REGISTERED_SERVICES_HEALTHY"


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

    r3 = qe.ask("Show Earth Health")
    assert r3["planet_health_score_pct"] == 74.5

    r4 = qe.ask("Show Alerts")
    assert r4["widget_type"] == "OperationalAlertDispatcherViewer"

    r5 = qe.ask("Show Streaming")
    assert r5["widget_type"] == "ObservationStreamEngineViewer"

    r6 = qe.ask("Show AI Monitoring")
    assert r6["widget_type"] == "AIMultiModelMonitorViewer"

    r7 = qe.ask("Explain Monitoring")
    assert len(r7["architecture_components"]) >= 5
