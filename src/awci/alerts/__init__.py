"""
Atmospheric Complexity Framework (ACF)

AWCI Alerts (``src/awci/alerts/``)

Real implementation start of the package named in
``docs/architecture/awci_reference_architecture.md`` section 19
("Alerts"), previously the specific gap named in
``docs/architecture/acf_awci_architecture_gap_analysis.md`` ("only a UI
panel (``awci_alerts_panel``), no standalone alerts engine").

Built 2026-09-21: ``engine.py`` (``AlertEngine``/``Alert`` - a real,
headless alert engine over ``awci.decision.situation.
SituationSnapshot``, usable outside the GUI dashboard) and
``notifications.py`` (``AlertNotifier`` - real, generic, in-process
subscriber dispatch, following the same real pattern already
established by ``awci.plugins.hooks.HookRegistry``).

``rules.py``/``thresholds.py``/``severity.py`` (the blueprint's
remaining named files) are deliberately not built - the real severity
bands/elevated-threshold rule this package's own ``engine.py`` uses
already exist as ``awci.decision.situation.AWCI_SCORE_BANDS``/
``ELEVATED_SCORE_BANDS``; a second copy here would be duplication.
``hazard_alerts.py``/``airport_alerts.py``/``route_alerts.py``/
``complexity_alerts.py`` are also not built - this codebase has no
real per-scope (airport-specific vs. route-specific vs. generic)
hazard taxonomy beyond what ``SituationSnapshot`` already provides, so
splitting ``engine.py`` into 4 files would add no real distinguishing
logic, only padding.
"""

from __future__ import annotations
