"""
Atmospheric Complexity Framework (ACF)

Global Operational Meteorological Center Platform Test Suite (MISSION ACF-030)
"""

from acf.ai.decision_support.operational_decision import OperationalDecisionSupportEngine
from acf.alerts.warning_engine import WarningEngine
from acf.connectors.live_connectors import LIVE_CONNECTORS_REGISTRY, LiveDataConnectorEngine
from acf.connectors.wmo_wis import WMOWISEngine
from acf.data.archive_system import OperationalArchiveSystem
from acf.forecast.forecast_engine import ForecastEngine
from acf.reports.briefings.briefing_generator import BriefingGenerator
from acf.science.query_engine import ScientificQueryEngine
from acf.verification.verification_engine import ForecastVerificationEngine
from acf.visualization.radar_satellite_center import OperationalRadarCenter, OperationalSatelliteCenter


def test_live_data_connectors():
    """Phase 1: Test des connecteurs de données opérationnelles en temps réel."""
    engine = LiveDataConnectorEngine()
    assert len(LIVE_CONNECTORS_REGISTRY) >= 6

    products = engine.fetch_catalog_products("noaa_nomads")
    assert any("GFS" in p for p in products)

    res = engine.sync_latest_dataset("ecmwf_opendata", "IFS 0.25° Global Forecasts")
    assert res["status"] == "success"
    assert res["checksum_verified"] is True


def test_wmo_wis_engine():
    """Phase 2: Test du système d'information WMO WIS 2.0 et GTS."""
    header = WMOWISEngine.parse_gts_header("SAFR31 LFPW 301500")
    assert header.cccc == "LFPW"
    assert "0-20000" in header.wigos_station_id

    oscar = WMOWISEngine.get_station_oscar_metadata(header.wigos_station_id)
    assert oscar["station_name"] == "PARIS-MONTSOURIS"


def test_radar_and_satellite_centers():
    """Phases 4 & 5: Test des centres opérationnels Radar et Satellite."""
    radar = OperationalRadarCenter()
    mosaic = radar.generate_radar_mosaic(["radar1.h5", "radar2.h5"])
    assert mosaic["status"] == "success"
    assert mosaic["max_reflectivity_dbz"] > 50.0

    sat = OperationalSatelliteCenter()
    rgb = sat.generate_rgb_composite("RGB_Day_Natural")
    assert rgb["status"] == "success"
    assert "MTG" in rgb["satellite"] or "SEVIRI" in rgb["satellite"]


def test_forecast_engine():
    """Phase 6: Test du moteur de prévision et d'assemblage NWP + IA."""
    f_engine = ForecastEngine()
    nowcast = f_engine.generate_nowcast({"max_reflectivity_dbz": 52.0}, [])
    assert nowcast["horizon"] == "Nowcasting (0-6 Hours)"
    assert nowcast["convective_trend"] == "Intensification"

    blended = f_engine.blend_forecasts({"temperature": 290.0}, {"temperature": 292.0}, weight_ai=0.5)
    assert abs(blended["blended_variables"]["temperature"] - 291.0) < 1e-4


def test_warning_engine():
    """Phase 7: Test du moteur d'alertes et vigilances opérationnelles."""
    w_engine = WarningEngine()
    alert = w_engine.issue_warning("Thunderstorm", "Orange", 85.0, ["Île-de-France", "Normandie"])
    assert alert.severity == "Orange"
    assert len(w_engine.get_active_warnings()) == 1


def test_briefing_generator():
    """Phase 8: Test de la génération automatique de briefings météo."""
    briefing = BriefingGenerator.generate_briefing("Morning Briefing", "Conditions calmes.")
    assert briefing["status"] == "generated"
    assert "# OFFICIAL METEOROLOGICAL BRIEFING" in briefing["content"]


def test_operational_decision_support():
    """Phase 10: Test du moteur d'aide à la décision opérationnelle."""
    engine = OperationalDecisionSupportEngine()
    eval_res = engine.evaluate_operational_situation({"CAPE": 2200.0}, {}, {}, {})
    assert eval_res["overall_risk_level"] in ["ÉLEVÉ", "CRITIQUE / EXTRÊME"]


def test_operational_decision_support_no_longer_fabricates_evidence():
    """
    Regression guard: evaluate_operational_situation() used to
    fabricate fixed "model_consensus" percentages and fake
    "supporting_observations" (a made-up METAR string, a made-up
    radiosonde reading) regardless of the actual ai_predictions/
    radar_summary/obs_data inputs (even when empty, as in the test
    above). It must now honestly report when no real data was
    supplied, and must genuinely reflect real data when it is.
    """
    engine = OperationalDecisionSupportEngine()

    empty_result = engine.evaluate_operational_situation({"CAPE": 2200.0}, {}, {}, {})
    assert empty_result["model_consensus"] == {"status": "NO_AI_PREDICTIONS_PROVIDED"}
    assert empty_result["supporting_observations"] == ["NO_OBSERVATIONS_PROVIDED"]
    # The old fabricated text must not appear anywhere.
    assert "GraphCast" not in str(empty_result)
    assert "22018G32KT" not in str(empty_result)

    real_result = engine.evaluate_operational_situation(
        {"CAPE": 2200.0},
        {"ifs_vs_graphcast_agreement_pct": 77.0},
        {"max_reflectivity_dbz": 55.0},
        {"metar_wind": "22018G32KT"},
    )
    assert real_result["model_consensus"] == {"ifs_vs_graphcast_agreement_pct": 77.0}
    assert "metar_wind: 22018G32KT" in real_result["supporting_observations"]
    assert "radar.max_reflectivity_dbz: 55.0" in real_result["supporting_observations"]


def test_forecast_verification_engine():
    """Phase 11: Test de la vérification statistique (POD, FAR, CSI, ETS, HSS)."""
    scores = ForecastVerificationEngine.contingency_table_metrics(a=40, b=10, c=5, d=45)
    assert scores["POD"] > 0.8
    assert scores["FAR"] < 0.3
    assert scores["CSI"] > 0.7
    assert scores["ETS"] > 0.0


def test_archive_system():
    """Phase 12: Test du système d'archivage et de rejeu (replay)."""
    archive = OperationalArchiveSystem()
    c_id = archive.archive_case_study("Storm Ciaran", "2023-11-02", "Severe wind storm", {}, {}, [])
    replayed = archive.replay_case_study(c_id)
    assert replayed is not None
    assert replayed["event_name"] == "Storm Ciaran"


def test_query_engine_phase13_operational_questions():
    """Phase 13: Test des requêtes naturelles du centre opérationnel."""
    q_engine = ScientificQueryEngine()

    r1 = q_engine.ask("Show radar")
    assert r1["layer_type"] == "radar_volume"

    r2 = q_engine.ask("Show satellite")
    assert r2["layer_type"] == "satellite_rgb"

    r3 = q_engine.ask("Generate briefing")
    assert r3["action"] == "generate_report"

    r4 = q_engine.ask("Explain warning")
    assert r4["severity"] == "ORANGE"
