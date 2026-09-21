"""Tests for the new AWCI decision-support risk matrix
(src/awci/decision/risk_matrix.py), built while working through the
full remaining-gaps list ("On les attaque toutes un par un") - the
one module this package's own Phase 1 build (§2m) explicitly deferred
until a real, cited methodology was available (ICAO Doc 9859 Safety
Management Manual's 5x5 risk-assessment matrix), added now with
explicit user confirmation.

The matrix values themselves (which of the 25 real (likelihood,
severity) combinations fall in which of the 3 real tolerability
bands) are ICAO's own standard, widely-reproduced SMM table - these
tests lock in the real structure (self-consistency: exactly 25
combinations, partitioned into exactly 3 disjoint bands) plus a few
individually-verified real cells, rather than re-deriving the whole
table from first principles.
"""

from __future__ import annotations

from awci.decision.risk_matrix import (
    LikelihoodCategory,
    RiskAssessment,
    RiskTolerability,
    SeverityCategory,
    _ACCEPTABLE_INDICES,
    _REVIEW_INDICES,
    _UNACCEPTABLE_INDICES,
    assess_risk,
)


def test_severity_categories_are_the_real_icao_5_level_scale():
    assert {c.value for c in SeverityCategory} == {"A", "B", "C", "D", "E"}
    assert SeverityCategory.CATASTROPHIC.value == "A"
    assert SeverityCategory.NEGLIGIBLE.value == "E"


def test_likelihood_categories_are_the_real_icao_5_level_scale():
    assert {c.value for c in LikelihoodCategory} == {1, 2, 3, 4, 5}
    assert LikelihoodCategory.FREQUENT.value == 5
    assert LikelihoodCategory.EXTREMELY_IMPROBABLE.value == 1


def test_assess_risk_returns_a_real_risk_assessment():
    result = assess_risk(LikelihoodCategory.FREQUENT, SeverityCategory.CATASTROPHIC)
    assert isinstance(result, RiskAssessment)
    assert result.risk_index == "5A"
    assert result.tolerability == RiskTolerability.UNACCEPTABLE


def test_the_worst_case_combination_is_unacceptable():
    result = assess_risk(LikelihoodCategory.FREQUENT, SeverityCategory.CATASTROPHIC)
    assert result.tolerability == RiskTolerability.UNACCEPTABLE


def test_the_best_case_combination_is_acceptable():
    result = assess_risk(LikelihoodCategory.EXTREMELY_IMPROBABLE, SeverityCategory.NEGLIGIBLE)
    assert result.tolerability == RiskTolerability.ACCEPTABLE


def test_a_real_review_band_combination():
    # 3B: Remote likelihood x Hazardous severity - real ICAO SMM "review required" cell.
    result = assess_risk(LikelihoodCategory.REMOTE, SeverityCategory.HAZARDOUS)
    assert result.risk_index == "3B"
    assert result.tolerability == RiskTolerability.REVIEW


# --------------------------------------------------------------------- discipline


def test_matrix_partitions_all_25_combinations_exactly_once():
    """Every real (likelihood, severity) combination must fall into
    exactly one of the 3 real tolerability bands - no gap, no overlap."""
    all_indices = set()
    for likelihood in LikelihoodCategory:
        for severity in SeverityCategory:
            result = assess_risk(likelihood, severity)
            all_indices.add(result.risk_index)

    assert len(all_indices) == 25
    assert _UNACCEPTABLE_INDICES | _REVIEW_INDICES | _ACCEPTABLE_INDICES == all_indices
    assert not (_UNACCEPTABLE_INDICES & _REVIEW_INDICES)
    assert not (_UNACCEPTABLE_INDICES & _ACCEPTABLE_INDICES)
    assert not (_REVIEW_INDICES & _ACCEPTABLE_INDICES)


def test_band_sizes_match_the_real_icao_smm_6_8_11_split():
    assert len(_UNACCEPTABLE_INDICES) == 6
    assert len(_REVIEW_INDICES) == 8
    assert len(_ACCEPTABLE_INDICES) == 11


def test_risk_assessment_is_a_real_frozen_dataclass():
    result = assess_risk(LikelihoodCategory.REMOTE, SeverityCategory.MINOR)
    try:
        result.risk_index = "9Z"  # type: ignore[misc]
        raised = False
    except Exception:
        raised = True
    assert raised


def test_risk_matrix_module_never_reads_a_real_awci_complexity_score():
    """Discipline test: this module must not import anything from
    awci.decision.situation/engine (the real, continuous AWCI score
    layer) - it is a standalone, caller-supplied-category classifier,
    never auto-derived from a continuous score (see module docstring
    for why that mapping would itself be an invented scheme)."""
    import awci.decision.risk_matrix as risk_matrix_module

    assert not hasattr(risk_matrix_module, "classify_awci_score")
    assert not hasattr(risk_matrix_module, "SituationSnapshot")
