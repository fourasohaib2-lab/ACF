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
    sat = SatelliteIngestor.ingest_satellite_stream("NOAA GOES")
    assert sat["status"] == "STREAM_INGESTED_SUCCESS"
    assert "Cloud Cover" in sat["variables_ingested"]

    qpe = RadarIngestor.compute_qpe_rainfall_rate(45.0)
    assert qpe > 0.0

    syn = SurfaceStationIngestor.ingest_synop_reports()
    assert syn["reports_count"] == 4500

    argo = OceanObservationIngestor.ingest_argo_profiles()
    assert argo["argo_floats_active"] == 3900


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
    state_vec = EarthAnalysisStateVector()
    summary = state_vec.get_analysis_summary()
    assert summary["status"] == "ANALYSIS_STATE_PRODUCED"
    assert summary["variables_count"] == 10

    neural_da = NeuralDataAssimilation.compute_ai_correction(0.42)
    assert neural_da["status"] == "NEURAL_ASSIMILATION_COMPLETE"
    assert neural_da["ai_correction_applied"] > 0.0


def test_data_catalog_and_streaming():
    """Test du catalogue de données multi-format et du moteur de streaming."""
    cat = DataCatalogEngine.get_catalog_summary()
    assert "GRIB2" in cat["supported_formats"]

    stream = StreamingEngine.get_stream_status()
    assert stream["status"] == "STREAMING_ACTIVE"
