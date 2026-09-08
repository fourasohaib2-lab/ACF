"""Unit test suite for ACF Observation Assimilation System (ACF-HPC-106).

REWRITTEN: this used to assert a cascade of fabricated "validated"
assimilation output (a fixed accepted-observation count regardless of
how many were submitted, fake BATOR/CANARI output paths, "SUCCESS"
status) presented as a real, operational AROME/ALADIN observation
assimilation pipeline - the same fake-stub pattern found and fixed
throughout this session, here in a real operational-NWP-adjacent
module. See assimilation_engine.py's NOTE (correction) docstrings for
what each stage used to fabricate.
"""

from acf.hpc_connector.assimilation.assimilation_engine import (
    ObservationAssimilationEngine,
    ObservationCatalog,
    QualityControl,
)


def test_assimilation_engine():
    engine = ObservationAssimilationEngine()
    res = engine.run_assimilation_pipeline(cycle="2026080300")
    assert res["status"] == "NOT_EXECUTED_NO_REAL_ASSIMILATION_BACKEND_CONNECTED"
    assert res["qc_metrics"]["accepted"] is None
    assert res["bator_output"] is None
    assert res["canari_output"] is None
    assert res["is_real_data"] is False


def test_observation_catalog_and_qc():
    cat = ObservationCatalog()
    obs = cat.list_observations()
    assert "SYNOP" in obs
    assert "AMDAR" in obs

    # CORRECTED: used to unconditionally claim "2418200 accepted" even
    # when called with obs_count=1000 (more accepted than submitted) -
    # no real QC rules are applied to any real observation data.
    qc = QualityControl()
    metrics = qc.apply_qc(1000)
    assert metrics["total"] == 1000
    assert metrics["accepted"] is None
    assert metrics["status"] == "NOT_CHECKED_NO_QC_RULES_APPLIED"
