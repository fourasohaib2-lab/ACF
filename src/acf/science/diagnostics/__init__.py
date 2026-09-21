"""
Atmospheric Complexity Framework (ACF)

Scientific Diagnostics Package

Migrated 2026-09-21 (Phase 7 of the ACF science/ per-domain
reorganization - see
docs/architecture/acf_awci_architecture_gap_analysis.md's own §4
section) from the single flat ``diagnostics.py`` module directly under
``acf.science``, matching the blueprint's own ``science/diagnostics/``
layer. Real module name kept as-is.

``diagnostics.py`` shares its own name with this package
(``acf.science.diagnostics``) - a flat shim file at the old
``src/acf/science/diagnostics.py`` path would be permanently shadowed
by this package directory and never actually importable (the same
real self-naming-collision bug already found and fixed for
``thermodynamics.py``/``stability.py``/``dynamics.py``/
``constants.py``/``radiation.py``/``boundary_layer.py`` in §4a-§4f).
There is no flat shim for it; this ``__init__.py`` re-exports both
real classes directly instead.
"""

from acf.science.diagnostics.diagnostics import DiagnosticAlert, SituationDiagnosis

__all__ = [
    "DiagnosticAlert",
    "SituationDiagnosis",
]
