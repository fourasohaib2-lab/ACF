"""
Regression tests against tests/data/golden/ - the Prompt Maître ACF
v2.0's section 31-32 "Golden Datasets" gap
(reports/ACF_MASTER_AUDIT_v2.md: "Aucun tests/data/golden/ - confirmé,
recherche vide"), and section 53's "categorie tests/scientific/
regression/ separee avec comparaison ancien/nouveau resultat
systematique" (also confirmed absent - this directory closes both).

Each test recomputes a real ACF result from a golden fixture's real
input and asserts it still matches the checked-in real reference
output - see tests/data/golden/README.md for why each fixture is safe
to snapshot (genuinely deterministic) and why a full solver run is
deliberately not one of them.
"""

from __future__ import annotations

import pytest

from acf.awci.calculator import AWCICalculator
from acf.science.encyclopedia.aerodynamics.isa_atmosphere import calculate_isa_pressure, calculate_isa_temperature
from acf.testing.golden import GoldenMismatchError, assert_matches_golden, load_golden


def test_isa_standard_atmosphere_matches_the_golden_reference():
    golden = load_golden("isa_standard_atmosphere.json")
    actual_points = [
        {
            "altitude_m": p["altitude_m"],
            "temperature_k": calculate_isa_temperature(p["altitude_m"]),
            "pressure_pa": calculate_isa_pressure(p["altitude_m"]),
        }
        for p in golden["points"]
    ]
    assert_matches_golden("isa_standard_atmosphere.json", {**golden, "points": actual_points})


def test_isa_standard_atmosphere_sea_level_is_exactly_the_icao_reference_constants():
    """Sanity check independent of the golden file itself: at z=0 the formula must reduce to exactly t0/p0."""
    assert calculate_isa_temperature(0.0) == 288.15
    assert calculate_isa_pressure(0.0) == 101325.0


def test_isa_standard_atmosphere_pressure_is_continuous_at_the_tropopause():
    """A real correctness property, not an arbitrary snapshot: the troposphere and stratosphere branches of calculate_isa_pressure() must agree at their z=11000m boundary."""
    just_below = calculate_isa_pressure(10999.999)
    just_above = calculate_isa_pressure(11000.0)
    assert just_below == pytest.approx(just_above, rel=1e-6)


def test_awci_calculator_matches_the_golden_reference_case():
    golden = load_golden("awci_calculator_reference_case.json")
    actual = AWCICalculator().calculate(golden["input"])
    assert_matches_golden("awci_calculator_reference_case.json", {**golden, "expected_output": actual})


def test_nwp_verification_metrics_matches_the_hand_computed_golden_case():
    from acf.verification.nwp_metrics import NWPVerificationMetrics

    golden = load_golden("nwp_verification_metrics_reference_case.json")
    actual = NWPVerificationMetrics.evaluate_all(golden["forecast"], golden["observation"], golden["threshold"])
    assert_matches_golden("nwp_verification_metrics_reference_case.json", {**golden, "expected_metrics": actual})


# ------------------------------------------------------------------ acf.testing.golden itself


def test_assert_matches_golden_passes_for_an_identical_value():
    golden = load_golden("nwp_verification_metrics_reference_case.json")
    assert_matches_golden("nwp_verification_metrics_reference_case.json", golden)  # no raise


def test_assert_matches_golden_reports_the_real_mismatch_path():
    golden = load_golden("nwp_verification_metrics_reference_case.json")
    broken = {**golden, "expected_metrics": {**golden["expected_metrics"], "rmse": 999.0}}

    with pytest.raises(GoldenMismatchError, match=r"expected_metrics\.rmse"):
        assert_matches_golden("nwp_verification_metrics_reference_case.json", broken)


def test_assert_matches_golden_tolerates_tiny_float_noise():
    golden = load_golden("nwp_verification_metrics_reference_case.json")
    noisy = {**golden, "expected_metrics": {**golden["expected_metrics"], "rmse": golden["expected_metrics"]["rmse"] + 1e-12}}
    assert_matches_golden("nwp_verification_metrics_reference_case.json", noisy)  # no raise


def test_assert_matches_golden_catches_a_missing_key():
    golden = load_golden("nwp_verification_metrics_reference_case.json")
    incomplete = dict(golden)
    del incomplete["threshold"]

    with pytest.raises(GoldenMismatchError, match="missing key"):
        assert_matches_golden("nwp_verification_metrics_reference_case.json", incomplete)


def test_load_golden_raises_a_clear_error_for_an_unknown_fixture():
    with pytest.raises(FileNotFoundError):
        load_golden("does_not_exist.json")
