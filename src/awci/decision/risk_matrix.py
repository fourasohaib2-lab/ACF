"""
Atmospheric Complexity Framework (ACF)

AWCI Decision Support - Risk Matrix

Real ICAO Doc 9859 (Safety Management Manual, SMM) 5x5 safety risk
assessment matrix - the ``risk_matrix.py`` module named in
``docs/architecture/awci_reference_architecture.md`` section 13,
deliberately deferred in this package's Phase 1 build (see this
package's own ``__init__.py``) until a real, cited methodology was
available rather than an ACF-invented scheme.

The 5 severity categories, 5 likelihood categories, and the resulting
15-band tolerability classification below are ICAO's own standard SMM
risk-assessment matrix - the same structure reproduced identically
across countless real aviation SMS manuals (ICAO Doc 9859, FAA
AC 120-92, EASA SMS guidance material). Self-consistency check: the 3
tolerability bands partition all 25 real (likelihood, severity)
combinations exactly once (6 Unacceptable + 8 Review + 11 Acceptable
= 25) - verified by a dedicated discipline test in this package's own
test file.

Deliberately NOT auto-derived from a real, continuous AWCI 0-100
complexity score: ICAO's own matrix operates on discrete, qualitative
safety-assessment categories a human safety analyst assigns from
operational judgement (real accident/incident likelihood, real
consequence severity) - inventing a numeric-score-to-SMS-category
mapping rule would itself be an ACF-invented scheme, exactly what this
package's Phase 1 scope decision explicitly avoided. A real caller
(a safety analyst, or a future real module with its own cited
likelihood/severity derivation) supplies both categories explicitly.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class SeverityCategory(Enum):
    """Real ICAO Doc 9859 SMM severity categories (Table, "Safety Risk
    Severity")."""

    CATASTROPHIC = "A"
    HAZARDOUS = "B"
    MAJOR = "C"
    MINOR = "D"
    NEGLIGIBLE = "E"


class LikelihoodCategory(Enum):
    """Real ICAO Doc 9859 SMM likelihood/probability categories
    (Table, "Safety Risk Probability")."""

    FREQUENT = 5
    OCCASIONAL = 4
    REMOTE = 3
    IMPROBABLE = 2
    EXTREMELY_IMPROBABLE = 1


class RiskTolerability(Enum):
    """Real ICAO Doc 9859 SMM tolerability bands (Table, "Safety Risk
    Tolerability")."""

    UNACCEPTABLE = "Unacceptable under the existing circumstances"
    REVIEW = "Acceptable based on risk mitigation - review required"
    ACCEPTABLE = "Acceptable"


#: Real ICAO Doc 9859 SMM risk-index -> tolerability-band mapping - the
#: standard 6/8/11-cell partition of all 25 (likelihood, severity)
#: combinations.
_UNACCEPTABLE_INDICES = frozenset({"5A", "5B", "5C", "4A", "4B", "3A"})
_REVIEW_INDICES = frozenset({"5D", "5E", "4C", "4D", "3B", "3C", "2A", "2B"})
_ACCEPTABLE_INDICES = frozenset(
    {"4E", "3D", "3E", "2C", "2D", "2E", "1A", "1B", "1C", "1D", "1E"}
)


@dataclass(frozen=True)
class RiskAssessment:
    """One real ICAO Doc 9859 SMM risk assessment - a real
    (likelihood, severity) pair classified into its real risk index
    and tolerability band."""

    likelihood: LikelihoodCategory
    severity: SeverityCategory
    risk_index: str
    tolerability: RiskTolerability


def assess_risk(likelihood: LikelihoodCategory, severity: SeverityCategory) -> RiskAssessment:
    """
    Real ICAO Doc 9859 SMM risk assessment - classifies a real,
    caller-supplied (likelihood, severity) pair into its real risk
    index (e.g. "5A") and real tolerability band.
    """
    risk_index = f"{likelihood.value}{severity.value}"
    if risk_index in _UNACCEPTABLE_INDICES:
        tolerability = RiskTolerability.UNACCEPTABLE
    elif risk_index in _REVIEW_INDICES:
        tolerability = RiskTolerability.REVIEW
    else:
        assert risk_index in _ACCEPTABLE_INDICES
        tolerability = RiskTolerability.ACCEPTABLE
    return RiskAssessment(likelihood=likelihood, severity=severity, risk_index=risk_index, tolerability=tolerability)
