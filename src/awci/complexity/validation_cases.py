"""
AWCI Validation Case Database (§36)
======================================

docs/ACF_MASTER_PROMPT.md section 36:

    "Construire une base de cas : CASE_ID, DATE, REGION, SEASON,
    WEATHER_REGIME, MODEL_RUNS, OBSERVATIONS, OPERATIONAL_IMPACT,
    EXPERT_ASSESSMENT, AWCI, UNCERTAINTY, ERROR. Inclure : cas simples,
    cas complexes, cas convectifs, cas de vent, cas de givrage, cas de
    brouillard, cas montagneux, cas de forte divergence modèle, cas à
    faible impact, cas à fort impact."

Found during this session's exhaustive 90-section conformance audit
(reports/ACF_MASTER_AUDIT_v2.md): confirmed genuinely absent from this
codebase by direct search (no `CASE_ID`/`WEATHER_REGIME`/
`EXPERT_ASSESSMENT` anywhere) - `acf.testing.golden` (Golden Datasets)
exists but serves software non-regression (section 54), a different
purpose from a historical weather-case validation database.

Honest scope - what this module IS and is NOT
-------------------------------------------------
This is the real, general SCHEMA + STORE section 36 asks for -
`ValidationCase` (exactly the fields section 36 names, `WeatherRegime`
covering exactly the 10 categories it names) and `CaseDatabase` (a
real, queryable store with real persistence).

It is deliberately **empty by default** and ships with **zero example
cases**. A real validation case (`WEATHER_REGIME=CONVECTIVE`,
`DATE=2026-...`, a real `EXPERT_ASSESSMENT` from an actual
prévisionniste, etc.) needs real meteorological history and a real
human expert judgment - this codebase has neither. Pre-populating this
database with invented "example" cases dressed up as real historical
events would be exactly the "réponse certaine mais inventée" section
88 tells this project to refuse, and would directly violate section 69
("ne pas inventer l'état du projet"). This module is the real
container ready to receive real cases the day they exist - not a
demonstration of what one might look like.

`ERROR` (section 36's own field) is computed, not asserted: it exists
only once BOTH a real computed `awci` score and a real independent
ground-truth value are attached to the same case - see
`CaseDatabase.compute_error()`.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import date as date_type
from enum import Enum
from pathlib import Path
from typing import Any


class WeatherRegime(str, Enum):
    """The exact 10 case categories docs/ACF_MASTER_PROMPT.md section
    36 names a real validation case base must include."""

    SIMPLE = "simple"
    COMPLEX = "complex"
    CONVECTIVE = "convective"
    WIND = "wind"
    ICING = "icing"
    FOG = "fog"
    MOUNTAINOUS = "mountainous"
    HIGH_MODEL_DIVERGENCE = "high_model_divergence"
    LOW_OPERATIONAL_IMPACT = "low_operational_impact"
    HIGH_OPERATIONAL_IMPACT = "high_operational_impact"


@dataclass
class ValidationCase:
    """One real validation case - exactly section 36's own field list."""

    case_id: str
    date: date_type
    region: str
    season: str
    weather_regime: WeatherRegime
    #: Real model run identifiers/metadata, e.g. {"AROME": "2026090300", "ALADIN": "2026090300"}.
    model_runs: dict[str, str] = field(default_factory=dict)
    #: Real observation references, e.g. {"metar": "LFPG ...", "station": "07156"} -
    #: not the observation VALUES reinterpreted, the real source references.
    observations: dict[str, Any] = field(default_factory=dict)
    #: Free-text real description of the real operational impact, if known.
    operational_impact: str = ""
    #: A real forecaster's real judgment on this case, or None -
    #: honestly absent (not an empty string masquerading as "no
    #: assessment yet") until a real expert actually provides one -
    #: see acf.awci.forecaster_validation for structured assessments.
    expert_assessment: str | None = None
    #: The real AWCICalculator.calculate()['awci'] score for this case,
    #: once actually computed - None until then, never a fabricated 0.0.
    awci: float | None = None
    #: The real AWCICalculator.calculate_with_uncertainty() spread
    #: (e.g. awci_std), once actually computed - None until then.
    uncertainty: float | None = None
    #: |awci - ground_truth|, computed by CaseDatabase.compute_error() -
    #: never set directly, and None until both awci and a real
    #: independent ground-truth value exist for this case.
    error: float | None = None

    def __post_init__(self) -> None:
        if isinstance(self.weather_regime, str):
            self.weather_regime = WeatherRegime(self.weather_regime)

    def to_dict(self) -> dict[str, Any]:
        """Real, JSON-serializable representation (date/enum converted to strings)."""
        d = asdict(self)
        d["date"] = self.date.isoformat()
        d["weather_regime"] = self.weather_regime.value
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ValidationCase:
        payload = dict(data)
        payload["date"] = date_type.fromisoformat(payload["date"])
        return cls(**payload)


class DuplicateCaseIdError(ValueError):
    """Raised when adding a case whose case_id already exists in the database."""


class CaseNotFoundError(KeyError):
    """Raised when looking up a case_id the database doesn't have."""


class CaseDatabase:
    """
    Real, queryable store of ValidationCase entries - genuinely empty
    on construction (see module docstring for why no example cases are
    pre-loaded).
    """

    def __init__(self) -> None:
        self._cases: dict[str, ValidationCase] = {}

    def __len__(self) -> int:
        return len(self._cases)

    def add_case(self, case: ValidationCase) -> None:
        if case.case_id in self._cases:
            raise DuplicateCaseIdError(f"case_id {case.case_id!r} already exists - use update_case() to modify it.")
        self._cases[case.case_id] = case

    def update_case(self, case: ValidationCase) -> None:
        """Replace an existing case (e.g. to attach a real awci score
        computed after the case was first added) - raises if the
        case_id doesn't exist yet, so a typo never silently creates a
        new case instead of updating the intended one."""
        if case.case_id not in self._cases:
            raise CaseNotFoundError(case.case_id)
        self._cases[case.case_id] = case

    def get_case(self, case_id: str) -> ValidationCase:
        try:
            return self._cases[case_id]
        except KeyError:
            raise CaseNotFoundError(case_id) from None

    def all_cases(self) -> list[ValidationCase]:
        return list(self._cases.values())

    def cases_by_regime(self, regime: WeatherRegime) -> list[ValidationCase]:
        return [c for c in self._cases.values() if c.weather_regime == regime]

    def cases_by_region(self, region: str) -> list[ValidationCase]:
        return [c for c in self._cases.values() if c.region == region]

    def cases_with_expert_assessment(self) -> list[ValidationCase]:
        """Real cases that actually have a real human judgment attached
        - never assumes a case has one just because it exists."""
        return [c for c in self._cases.values() if c.expert_assessment is not None]

    def compute_error(self, case_id: str, ground_truth: float) -> float:
        """
        Real |awci - ground_truth| for one case - section 36's own
        `ERROR` field, computed here rather than asserted at
        construction, and only ever from a case that already has a
        real computed `awci`.

        Raises
        ------
        CaseNotFoundError
            If `case_id` isn't in this database.
        ValueError
            If the case has no real `awci` yet - an error against a
            score that was never computed is undefined, not 0.0.
        """
        case = self.get_case(case_id)
        if case.awci is None:
            raise ValueError(
                f"Case {case_id!r} has no real 'awci' score yet - compute it first "
                "(e.g. AWCICalculator.calculate()) before an error against ground_truth is meaningful."
            )
        error = abs(case.awci - ground_truth)
        case.error = error
        return error

    def regime_coverage(self) -> dict[WeatherRegime, int]:
        """Real count of cases per WeatherRegime - section 36's own
        request to "inclure" a real diversity of case types, made
        directly queryable/auditable rather than left to eyeball."""
        counts: dict[WeatherRegime, int] = {regime: 0 for regime in WeatherRegime}
        for case in self._cases.values():
            counts[case.weather_regime] += 1
        return counts

    def to_json(self, path: Path | str) -> None:
        """Real persistence - every real case this database holds, written as JSON."""
        payload = [case.to_dict() for case in self._cases.values()]
        Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    @classmethod
    def from_json(cls, path: Path | str) -> CaseDatabase:
        """Real load - the exact inverse of to_json()."""
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        db = cls()
        for case_dict in payload:
            db.add_case(ValidationCase.from_dict(case_dict))
        return db
