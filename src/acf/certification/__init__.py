"""
ACF Certification Engine
=========================

Explicit user request: the "Prompt Maître ACF v2.0" master specification's
section 32 describes a formal Certification Engine - a pipeline
(INPUT VALID -> QC PASS -> PHYSICS PASS -> SCIENCE PASS -> PROVENANCE
PASS -> VERIFICATION STATUS -> CERTIFICATION) that decides whether one
data product is fit to publish. reports/ACF_MASTER_AUDIT_v2.md found
this genuinely absent: `acf.master.scientific_certification.
ScientificCertificationEngine` is a real, honestly-disclosed-as-
unimplemented audit of ACF's own equation *library*, a different
concept from certifying one *data product*.

This package is the fifth-priority item finished (after Physics Guard,
the Data Contract, the Model Adapter Protocol, the Event Engine and the
Verification pipeline + Model Skill Database) - and deliberately its
last-built piece, since every real step it runs is borrowed from one of
those: `Dataset.is_fully_documented()`/`Dataset.validate()`/
`Provenance.is_complete()` from the Data Contract, `PhysicsGuard` (via
`Dataset.validate()`) from the Physics Guard, `ModelSkillDatabase` from
the Verification pipeline, and `Event.transition_to()` from the Event
Engine for the one real, live VERIFIED -> CERTIFIED wiring
(`CertificationEngine.certify_event()`).

See `acf.certification.engine` for the real pipeline and its honest
scope (which steps are only applicable when a caller actually supplies
the data they need, e.g. `science_pass` needs a `VariableContract`).
"""

from acf.certification.engine import CertificationEngine, CertificationReport, CertificationStepResult

__all__ = ["CertificationEngine", "CertificationReport", "CertificationStepResult"]
