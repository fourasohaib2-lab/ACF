"""
AWCI Validation Against Human Forecaster Expertise (§37)
============================================================

docs/ACF_MASTER_PROMPT.md section 37:

    "L'AWCI doit être comparé à l'évaluation de prévisionnistes. Mais
    attention : l'avis humain n'est pas automatiquement une vérité
    absolue. Il constitue une référence experte à caractériser. Étudier :
    accord, désaccord, biais, reproductibilité, variabilité
    inter-prévisionnistes."

Found during this session's exhaustive 90-section conformance audit
(reports/ACF_MASTER_AUDIT_v2.md): confirmed genuinely absent - no
structured comparison against human forecaster judgment, no inter-rater
agreement statistic anywhere in this codebase (direct search for
"cohen_kappa"/"inter_rater" found nothing).

Honest scope - what this module IS and is NOT
-------------------------------------------------
This is the real, general STATISTICAL INFRASTRUCTURE section 37 asks
for - a `ForecasterAssessment` record for one real human judgment on
one real case, plus real, well-established inter-rater agreement
statistics (Cohen's kappa for categorical agreement - a real,
published formula, not invented here - see `cohens_kappa()`'s own
docstring for the reference derivation and a worked textbook check in
this module's own test suite) applicable to:
- AWCI-vs-forecaster agreement (section 37's own "accord, désaccord,
  biais" - is the real computed AWCI level consistent with what a real
  forecaster judged?).
- forecaster-vs-forecaster agreement (section 37's own "variabilité
  inter-prévisionnistes" - do two real forecasters agree with each
  other on the same case, independent of AWCI entirely?).

This module contains **zero real forecaster assessments** and
**computes nothing about any real case** until a caller supplies real
ones. No synthetic "example forecaster" opinion is invented here or
pre-loaded - see acf.awci.validation_cases's own module docstring for
the identical reasoning applied there. `bias()`/`rmse()`/`mae()` for
CONTINUOUS score comparisons are not reimplemented here - reuse
acf.verification.nwp_metrics.NWPVerificationMetrics directly for those
(this module supplies real CATEGORICAL agreement statistics that
codebase didn't have).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass


@dataclass
class ForecasterAssessment:
    """One real human forecaster's real judgment on one real
    validation case (acf.awci.validation_cases.ValidationCase's own
    `case_id`)."""

    case_id: str
    forecaster_id: str
    #: The real complexity level this forecaster assigned - expected to
    #: match one of AWCICalculator.LEVEL_THRESHOLDS' own labels (e.g.
    #: "Moderate", "High") for a real, directly comparable categorical
    #: judgment, though this dataclass does not itself enforce that
    #: (a forecaster's own real vocabulary may differ - see
    #: agreement_fraction()/cohens_kappa() for how mismatched
    #: vocabularies are handled: as genuine disagreement, not an error).
    assessed_level: str
    #: An optional real numeric score, if this forecaster gave one -
    #: None (not 0.0) when they only gave a categorical judgment.
    assessed_score: float | None = None
    notes: str = ""


def agreement_fraction(ratings_a: Sequence[str], ratings_b: Sequence[str]) -> float:
    """
    Real observed proportion of exact agreement between two real
    categorical rating sequences (section 37's own "accord/désaccord"),
    aligned by index.

    Raises
    ------
    ValueError
        If the two sequences have different lengths, or if empty.
    """
    if len(ratings_a) != len(ratings_b):
        raise ValueError(f"ratings_a and ratings_b must have the same length, got {len(ratings_a)} and {len(ratings_b)}")
    if not ratings_a:
        raise ValueError("ratings_a/ratings_b must not be empty - agreement is undefined over zero real cases.")
    matches = sum(1 for a, b in zip(ratings_a, ratings_b, strict=True) if a == b)
    return matches / len(ratings_a)


def cohens_kappa(ratings_a: Sequence[str], ratings_b: Sequence[str]) -> float:
    """
    Real Cohen's kappa (Cohen, 1960) - the standard, published
    inter-rater agreement statistic for categorical judgments, correcting
    observed agreement for the agreement expected by chance alone (two
    raters who agree 90% of the time on a category 89% of cases fall
    into are not demonstrating real skill at agreeing - kappa reflects
    that; a raw agreement_fraction() does not).

        kappa = (p_o - p_e) / (1 - p_e)

        p_o = observed agreement fraction (this module's own
              agreement_fraction()).
        p_e = expected-by-chance agreement = sum over every real
              category c actually observed of
              P(rater_a assigns c) * P(rater_b assigns c).

    Used here for BOTH section 37 use cases with the same real formula:
    AWCI-level-vs-forecaster-assessment agreement, and
    forecaster-vs-forecaster agreement (inter-rater variability).

    Returns
    -------
    float
        1.0 = perfect real agreement, 0.0 = exactly chance-level
        agreement, negative = real agreement worse than chance. Returns
        1.0 (not NaN/an exception) in the real degenerate case where
        every single rating - from both raters - is the exact same one
        category (p_e = 1.0, so the formula's own denominator would be
        zero): both raters trivially agree on everything, a real,
        well-defined edge case, not a computation failure.

    Raises
    ------
    ValueError
        If the two sequences have different lengths, or are empty -
        same real guard as agreement_fraction().
    """
    if len(ratings_a) != len(ratings_b):
        raise ValueError(f"ratings_a and ratings_b must have the same length, got {len(ratings_a)} and {len(ratings_b)}")
    if not ratings_a:
        raise ValueError("ratings_a/ratings_b must not be empty - kappa is undefined over zero real cases.")

    n = len(ratings_a)
    p_o = agreement_fraction(ratings_a, ratings_b)

    categories = set(ratings_a) | set(ratings_b)
    p_e = 0.0
    for category in categories:
        p_a = sum(1 for r in ratings_a if r == category) / n
        p_b = sum(1 for r in ratings_b if r == category) / n
        p_e += p_a * p_b

    if p_e >= 1.0:
        # Both raters assigned the exact same single category to every
        # real case - real, trivial total agreement, not a division by
        # (1 - p_e) = 0 computation failure.
        return 1.0
    return (p_o - p_e) / (1.0 - p_e)


def inter_forecaster_variability(assessments_by_forecaster: dict[str, Sequence[str]]) -> dict[str, float]:
    """
    Real pairwise Cohen's kappa between every pair of real forecasters
    in `assessments_by_forecaster` (section 37's own "variabilité
    inter-prévisionnistes") - each forecaster's sequence must already
    be aligned to the same real, ordered set of case IDs (this function
    does not itself track case IDs - see
    acf.awci.validation_cases.CaseDatabase for that).

    Parameters
    ----------
    assessments_by_forecaster : dict[str, sequence of str]
        Real forecaster_id -> their real assessed_level per case, all
        sequences the same real length and case order.

    Returns
    -------
    dict[str, float]
        Keyed by "forecaster_a vs forecaster_b" (alphabetically
        ordered pair, so the same pair never appears twice under two
        different key spellings), real Cohen's kappa per pair.

    Raises
    ------
    ValueError
        If fewer than 2 forecasters are supplied - inter-forecaster
        variability is undefined for 1 or 0 real forecasters.
    """
    forecaster_ids = sorted(assessments_by_forecaster)
    if len(forecaster_ids) < 2:
        raise ValueError(
            f"inter_forecaster_variability() needs at least 2 real forecasters, got {len(forecaster_ids)}."
        )
    results: dict[str, float] = {}
    for i, a in enumerate(forecaster_ids):
        for b in forecaster_ids[i + 1 :]:
            results[f"{a} vs {b}"] = cohens_kappa(assessments_by_forecaster[a], assessments_by_forecaster[b])
    return results
