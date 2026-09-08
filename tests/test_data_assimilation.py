"""
Global Earth Data Assimilation Framework Test Suite (MISSION ACF-DT-002)
"""

import pytest

from acf.ai.data_assimilation.neural_assimilation import NeuralDataAssimilation
from acf.data.data_catalog import DataCatalogEngine
from acf.data.streaming import StreamingEngine
from acf.data_assimilation.analysis_state import EarthAnalysisStateVector
from acf.data_assimilation.assimilation.ensemble.enkf import EnsembleKalmanFilter
from acf.data_assimilation.assimilation.hybrid.hybrid_da import HybridEnsembleVarDA
from acf.data_assimilation.assimilation.variational.var_4d import FourDVarEngine
from acf.data_assimilation.observation_ingestion.ocean_observation_ingestor import OceanObservationIngestor
from acf.data_assimilation.observation_ingestion.radar_ingestor import RadarIngestor
from acf.data_assimilation.observation_ingestion.satellite_ingestor import SatelliteIngestor
from acf.data_assimilation.observation_ingestion.surface_station_ingestor import SurfaceStationIngestor
from acf.data_assimilation.quality_control.bias_correction import VariationalBiasCorrection
from acf.data_assimilation.quality_control.observation_error import ObservationErrorModel
from acf.data_assimilation.quality_control.qc_engine import ObservationQCEngine


def test_observation_ingestion_engine():
    """Test de l'ingestion des satellites, radars, stations sol et bouées océaniques ARGO."""
    # CORRECTED: constellation was genuinely echoed, but this used to
    # also claim 4 fixed "variables_ingested" and "STREAM_INGESTED_SUCCESS"
    # with 0 real satellite data connection.
    sat = SatelliteIngestor.ingest_satellite_stream("NOAA GOES")
    assert sat["status"] == "NOT_INGESTED_NO_SATELLITE_DATA_CONNECTION"
    assert sat["variables_ingested"] == []

    qpe = RadarIngestor.compute_qpe_rainfall_rate(45.0)
    assert qpe > 0.0

    # CORRECTED: used to unconditionally claim a fixed "4500"
    # reports_count and "REPORTS_INGESTED" with 0 real GTS/WIS
    # connection - same pattern as satellite_ingestor.py above.
    syn = SurfaceStationIngestor.ingest_synop_reports()
    assert syn["reports_count"] is None
    assert syn["status"] == "NOT_INGESTED_NO_STATION_DATA_CONNECTION"

    # CORRECTED: used to unconditionally claim a fixed "3900"
    # argo_floats_active and "ARGO_PROFILES_INGESTED" with 0 real
    # connection to the Argo GDAC/GTS distribution.
    argo = OceanObservationIngestor.ingest_argo_profiles()
    assert argo["argo_floats_active"] is None
    assert argo["status"] == "NOT_INGESTED_NO_ARGO_DATA_CONNECTION"


def test_quality_control_and_error_modeling():
    """Test du contrôle qualité (Range Check -90°C < T < +60°C), modèle d'erreur et VarBC."""
    assert ObservationQCEngine.validate_temperature_observation(25.0) is True
    assert ObservationQCEngine.validate_temperature_observation(-120.0) is False

    qc = ObservationQCEngine.run_qc_pipeline([{"temp_c": 15.0}, {"temp_c": -150.0}])
    assert qc["passed_qc_count"] == 1

    err_std = ObservationErrorModel.get_observation_error_std("SYNOP_Thermometer")
    assert err_std == 0.2

    corrected = VariationalBiasCorrection.correct_bias(285.5, 0.5)
    assert corrected == 285.0


def test_assimilation_algorithms_4dvar_enkf_hybrid():
    """Test des algorithmes d'assimilation 4D-Var, EnKF 50 membres et 4DEnVar Hybride."""
    # compute_cost_function() is a real, correct scalar 4D-Var cost
    # function implementation - unaffected by the corrections below.
    cost = FourDVarEngine.compute_cost_function(1.0, 2.0)
    assert cost > 0.0

    # CORRECTED: minimize_4dvar()/run_ensemble_update()/
    # run_hybrid_assimilation() used to unconditionally claim
    # CONVERGED_OPTIMAL / ENKF_UPDATE_SUCCESS / HYBRID_ASSIMILATION_SUCCESS
    # with zero real minimization, ensemble, or hybrid covariance
    # computation behind any of them - direct fabrication of the exact
    # NWP data assimilation methods (4D-Var, EnKF, hybrid 4DEnVar) this
    # whole project is meant to provide. None of the underlying
    # infrastructure (adjoint models, ensemble covariances, real
    # optimizers) exists yet, so they now honestly raise
    # NotImplementedError instead of fabricating convergence.
    with pytest.raises(NotImplementedError):
        FourDVarEngine.minimize_4dvar()

    with pytest.raises(NotImplementedError):
        EnsembleKalmanFilter.run_ensemble_update(50)

    with pytest.raises(NotImplementedError):
        HybridEnsembleVarDA.run_hybrid_assimilation(0.5)


def test_analysis_state_vector_and_neural_da():
    """Test du vecteur d'état global ré-assimilé X et de l'assimilation neuronale PINN/GNN."""
    # CORRECTED: used to default analysis_timestamp/quality_score to a
    # fixed "2026-08-02 12:00 UTC" / "98.6" and unconditionally claim
    # "ANALYSIS_STATE_PRODUCED" - no DA engine in this package can
    # actually produce a real analysis yet (EnKF/4D-Var/Hybrid all
    # raise NotImplementedError, tested above).
    state_vec = EarthAnalysisStateVector()
    summary = state_vec.get_analysis_summary()
    assert summary["status"] == "NOT_PRODUCED_NO_REAL_ASSIMILATION_CONNECTED"
    assert summary["is_real_data"] is False
    assert summary["analysis_quality_score"] is None
    assert summary["variables_count"] == 10

    produced_state = EarthAnalysisStateVector(analysis_timestamp="2026-09-01 00:00 UTC", quality_score=91.2)
    produced_summary = produced_state.get_analysis_summary()
    assert produced_summary["status"] == "ANALYSIS_STATE_PRODUCED"
    assert produced_summary["is_real_data"] is True

    # CORRECTED: used to multiply innovation_vector by a fixed 0.85 and
    # present the result as a "Physics-Informed Graph Neural Network"
    # correction - no neural network of any kind is trained or
    # evaluated anywhere in this codebase.
    neural_da = NeuralDataAssimilation.compute_ai_correction(0.42)
    assert neural_da["status"] == "NOT_CORRECTED_NO_TRAINED_MODEL_CONNECTED"
    assert neural_da["ai_correction_applied"] is None
    assert neural_da["innovation_input"] == 0.42  # genuinely echoed


def test_data_catalog_and_streaming():
    """Test du catalogue de données multi-format et du moteur de streaming."""
    # CORRECTED: supported_formats is a genuine static declared scope,
    # but status used to claim "DATA_CATALOG_ACTIVE" - no real storage
    # backend is connected.
    cat = DataCatalogEngine.get_catalog_summary()
    assert "GRIB2" in cat["supported_formats"]
    assert cat["status"] == "NOT_CONNECTED_NO_STORAGE_BACKEND_CONFIGURED"

    # CORRECTED: used to claim a fabricated "128.5 Mbps" live
    # throughput and "STREAMING_ACTIVE" - no real streaming connection
    # exists.
    stream = StreamingEngine.get_stream_status()
    assert stream["status"] == "NOT_STREAMING_NO_CONNECTION_ESTABLISHED"
    assert stream["throughput_mbps"] is None
