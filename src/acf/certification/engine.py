"""
CertificationEngine: the Prompt Maître ACF v2.0's section 32 product
certification pipeline -
INPUT VALID -> QC PASS -> PHYSICS PASS -> SCIENCE PASS -> PROVENANCE
PASS -> VERIFICATION STATUS -> CERTIFICATION.

reports/ACF_MASTER_AUDIT_v2.md found `acf.master.scientific_certification.
ScientificCertificationEngine` real but a different thing entirely - an
(honestly-disclosed-as-not-implemented) audit of ACF's own equation
library, not a pipeline that certifies one data product. And it found
no certification pipeline at all: "aucun pipeline INPUT VALID -> ... ->
CERTIFICATION comme objet réutilisable."

This is deliberately NOT a sixth parallel implementation of any check -
every step below calls a real, already-existing ACF method:

- INPUT VALID  : Dataset.is_fully_documented() (acf.core.contracts).
- QC PASS      : Dataset.quality.status (acf.core.contracts.QualityInfo)
                 - requires a genuine "PASS", never silently implied.
- PHYSICS PASS : Dataset.validate(), which itself reuses PhysicsGuard -
                 not called a second time here.
- SCIENCE PASS : real only when a VariableContract is supplied, checks
                 Dataset.values against its real valid_range. No
                 unified "science engine" exists anywhere in ACF today
                 (reports/ACF_MASTER_AUDIT_v2.md: "Diagnostics
                 unifiés: PARTIAL, dispersé") - this step is honestly
                 marked not-applicable rather than invented when no
                 contract is given.
- PROVENANCE PASS : Provenance.is_complete() (acf.core.contracts).
- VERIFICATION STATUS : ModelSkillDatabase.mean_skill() (acf.verification)
                 against a caller-supplied acceptance threshold - real
                 only when both are configured and real history exists
                 for this dataset's model/variable; otherwise honestly
                 not-applicable, never a fabricated pass.

A dataset is CERTIFIED only if every step that was actually applicable
passed - a step nobody configured data for does not count against or
for it, and is never silently treated as a pass.

Branché réellement, pas juste construit à côté: `certify_event()` below
drives a real `acf.events.event.Event`'s VERIFIED -> CERTIFIED
transition - the only transition CertificationEngine has any business
making, per Event's own lifecycle diagram (it doesn't add or bypass any
edge in `acf.events.event._LEGAL_TRANSITIONS`; a REJECTED report simply
leaves the Event at VERIFIED, since VERIFIED has no REJECTED edge to
begin with).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from acf.core.contracts.dataset import Dataset
from acf.core.contracts.variable import VariableContract
from acf.events.event import Event
from acf.verification.skill_database import ModelSkillDatabase

#: Ordered per the Prompt Maître's own §32 pipeline name - CERTIFICATION
#: itself is the aggregate decision, not a step in this list.
_STEP_ORDER = (
    "input_valid",
    "qc_pass",
    "physics_pass",
    "science_pass",
    "provenance_pass",
    "verification_status",
)


@dataclass
class CertificationStepResult:
    """Outcome of one real §32 pipeline step."""

    name: str
    #: False for a step nobody configured data for (e.g. no
    #: VariableContract given for science_pass) - never counted for or
    #: against the final decision.
    applicable: bool
    passed: bool
    detail: str


@dataclass
class CertificationReport:
    """Real outcome of one CertificationEngine.certify() call."""

    dataset_id: str
    decision: str  # "CERTIFIED" | "REJECTED"
    steps: list[CertificationStepResult] = field(default_factory=list)

    def step(self, name: str) -> CertificationStepResult:
        for s in self.steps:
            if s.name == name:
                return s
        raise KeyError(name)

    def failed_steps(self) -> list[CertificationStepResult]:
        """Only the applicable steps that actually failed - what an operator needs to see to understand a REJECTED decision."""
        return [s for s in self.steps if s.applicable and not s.passed]


class CertificationEngine:
    """
    Runs the real §32 pipeline on one `Dataset`, reusing ACF's existing
    building blocks (see module docstring for exactly which method each
    step calls).
    """

    def __init__(
        self,
        skill_database: ModelSkillDatabase | None = None,
        max_acceptable_error: float | None = None,
    ) -> None:
        """
        Parameters
        ----------
        skill_database : optional real acf.verification.skill_database.ModelSkillDatabase.
            When given together with `max_acceptable_error`, enables
            the real VERIFICATION STATUS step.
        max_acceptable_error : optional float.
            Maximum acceptable mean value of the verification `metric`
            (see certify()) for VERIFICATION STATUS to pass - a
            caller-declared operational threshold, not a value this
            engine invents.
        """
        self.skill_database = skill_database
        self.max_acceptable_error = max_acceptable_error

    def certify(
        self,
        dataset: Dataset,
        variable_contract: VariableContract | None = None,
        metric: str = "rmse",
    ) -> CertificationReport:
        """Run every real §32 step on `dataset` and return the aggregate decision."""
        steps: list[CertificationStepResult] = [
            self._input_valid(dataset),
            self._qc_pass(dataset),
            self._physics_pass(dataset),
            self._science_pass(dataset, variable_contract),
            self._provenance_pass(dataset),
            self._verification_status(dataset, metric),
        ]
        decision = "CERTIFIED" if all(s.passed for s in steps if s.applicable) else "REJECTED"
        return CertificationReport(dataset_id=dataset.id, decision=decision, steps=steps)

    def certify_event(
        self,
        event: Event,
        dataset: Dataset,
        variable_contract: VariableContract | None = None,
        metric: str = "rmse",
    ) -> CertificationReport:
        """
        Certify `dataset` and, if CERTIFIED, genuinely advance `event`
        from VERIFIED to CERTIFIED via `Event.transition_to()` - the
        real "vivant" link between this pipeline and the Event Engine.

        Raises
        ------
        ValueError
            If `event` is not currently in VERIFIED status - certifying
            an event that hasn't gone through its own real lifecycle
            up to VERIFIED first would bypass that lifecycle, which
            this method refuses to do.
        """
        if event.status != "VERIFIED":
            raise ValueError(f"event must be in VERIFIED status to certify, got {event.status!r} (event_id={event.event_id})")
        report = self.certify(dataset, variable_contract=variable_contract, metric=metric)
        if report.decision == "CERTIFIED":
            event.transition_to("CERTIFIED")
        return report

    # ------------------------------------------------------------ steps

    @staticmethod
    def _input_valid(dataset: Dataset) -> CertificationStepResult:
        ok = dataset.is_fully_documented()
        return CertificationStepResult(
            "input_valid",
            applicable=True,
            passed=ok,
            detail="Dataset.is_fully_documented()" if ok else "Dataset is missing required metadata - see Dataset.is_fully_documented()",
        )

    @staticmethod
    def _qc_pass(dataset: Dataset) -> CertificationStepResult:
        status = dataset.quality.status
        return CertificationStepResult(
            "qc_pass",
            applicable=True,
            passed=(status == "PASS"),
            detail=f"Dataset.quality.status={status!r}",
        )

    @staticmethod
    def _physics_pass(dataset: Dataset) -> CertificationStepResult:
        guard_report = dataset.validate()
        return CertificationStepResult(
            "physics_pass",
            applicable=True,
            passed=guard_report.passed,
            detail="; ".join(guard_report.violations) if guard_report.violations else f"PhysicsGuard: {guard_report.checks_run} all passed",
        )

    @staticmethod
    def _science_pass(dataset: Dataset, contract: VariableContract | None) -> CertificationStepResult:
        if contract is None:
            return CertificationStepResult(
                "science_pass", applicable=False, passed=False, detail="no VariableContract supplied - not assessed"
            )
        if contract.valid_range is None:
            return CertificationStepResult(
                "science_pass",
                applicable=False,
                passed=False,
                detail=f"{contract.standard_name!r} has no documented valid_range - not assessed",
            )
        if dataset.values is None:
            return CertificationStepResult(
                "science_pass", applicable=True, passed=False, detail="Dataset has no values to check against valid_range"
            )
        values = np.asarray(dataset.values, dtype=float)
        lo, hi = contract.valid_range
        n_out = int(np.sum((values < lo) | (values > hi)))
        return CertificationStepResult(
            "science_pass",
            applicable=True,
            passed=(n_out == 0),
            detail=(
                f"all values within {contract.name}'s valid_range {contract.valid_range} {contract.unit}"
                if n_out == 0
                else f"{n_out} value(s) outside {contract.name}'s valid_range {contract.valid_range} {contract.unit}"
            ),
        )

    @staticmethod
    def _provenance_pass(dataset: Dataset) -> CertificationStepResult:
        if dataset.provenance is None:
            return CertificationStepResult("provenance_pass", applicable=True, passed=False, detail="no Provenance attached to this Dataset")
        ok = dataset.provenance.is_complete()
        return CertificationStepResult(
            "provenance_pass",
            applicable=True,
            passed=ok,
            detail="all provenance version fields set" if ok else "provenance incomplete - some version field left at 'unknown'",
        )

    def _verification_status(self, dataset: Dataset, metric: str) -> CertificationStepResult:
        if self.skill_database is None or self.max_acceptable_error is None:
            return CertificationStepResult(
                "verification_status",
                applicable=False,
                passed=False,
                detail="no skill_database/max_acceptable_error configured on this CertificationEngine - not assessed",
            )
        skill = self.skill_database.mean_skill(dataset.model, dataset.variable, metric)
        if skill is None:
            return CertificationStepResult(
                "verification_status",
                applicable=False,
                passed=False,
                detail=f"no recorded {metric!r} history for model={dataset.model!r} variable={dataset.variable!r} - not assessed",
            )
        ok = skill <= self.max_acceptable_error
        return CertificationStepResult(
            "verification_status",
            applicable=True,
            passed=ok,
            detail=f"mean {metric}={skill:.6g} vs max_acceptable_error={self.max_acceptable_error:.6g}",
        )
