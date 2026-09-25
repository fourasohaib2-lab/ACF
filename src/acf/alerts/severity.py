"""
Atmospheric Complexity Framework (ACF)

Alerts - Severity

Real severity-level helpers - the ``severity.py`` module named in
``docs/architecture/acf_awci_architecture_gap_analysis.md`` (row
``alerts/`` -> blueprint's ``engine/rules/thresholds/events/
notification/severity`` split). ``SEVERITY_ORDER`` is exactly the
real 3-level WMO/EUMETNET CAP vocabulary
``acf.alerts.warning_engine.OperationalWarning.severity`` already
documents in its own field comment ("Yellow"/"Orange"/"Red") - not a
new, independently invented scale.
"""

from __future__ import annotations

#: Real, ascending severity order - the exact same 3 real levels
#: already used by every OperationalWarning.severity value in this
#: codebase (see that dataclass's own field comment).
SEVERITY_ORDER: tuple[str, ...] = ("Yellow", "Orange", "Red")


def severity_rank(severity: str) -> int:
    """Real ordinal rank of a real severity level (0 = Yellow, 2 = Red).

    Raises
    ------
    ValueError
        If ``severity`` is not one of ``SEVERITY_ORDER`` - never
        guesses a rank for an unrecognized level.
    """
    try:
        return SEVERITY_ORDER.index(severity)
    except ValueError as exc:
        raise ValueError(f"{severity!r} is not a real severity level - expected one of {SEVERITY_ORDER}") from exc


def is_at_least(severity: str, threshold: str) -> bool:
    """Real comparison - ``True`` when ``severity`` is at least as
    severe as ``threshold`` (e.g. ``is_at_least("Orange", "Yellow")``
    is ``True``)."""
    return severity_rank(severity) >= severity_rank(threshold)
