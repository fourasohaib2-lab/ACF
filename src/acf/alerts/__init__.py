"""
acf.alerts - WarningEngine/OperationalWarning (warning_engine.py), a
real WMO/EUMETNET-CAP-style warning issuance engine (real UUIDs, real
datetime validity windows). Already carries its own fix disclosures
(fake AI-confirmation default, fabricated validity window - both
removed by earlier passes). Genuinely used by acf.geology.
earthquake_warning (verified by grep) - not disconnected.

Added 2026-09-21 to close this project's own blueprint `alerts/{...}`
gap (`docs/architecture/acf_awci_architecture_gap_analysis.md`):
`severity.py` (`SEVERITY_ORDER`/`severity_rank()`/`is_at_least()` -
the exact real 3-level Yellow/Orange/Red vocabulary
`OperationalWarning.severity` already uses) and `notification.py`
(`WarningNotifier` - real in-process dispatch, same pattern as
`awci.alerts.notifications.AlertNotifier`). `rules.py`/`thresholds.py`
are deliberately not built - `WarningEngine.issue_warning()` takes
severity/probability as caller-supplied values with no internal
per-phenomenon threshold table to extract; inventing specific
numeric thresholds here would be fabrication, not a real gap closure.
`events.py` is deliberately not built - wiring `WarningEngine` to emit
real lifecycle events would mean modifying that already-tested class,
out of this item's minimal-change scope.
"""
