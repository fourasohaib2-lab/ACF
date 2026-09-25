"""AWCI dashboard - the real, operational aviation complexity GUI.

Migrated 2026-09-21 (Phase 10 of the AWCI separate-package migration -
see ``awci``'s own package docstring and
``docs/architecture/acf_awci_architecture_gap_analysis.md``) from
``acf.gui.dashboard`` - the 29 ``awci_*.py`` modules that made up the
real AWCI dashboard (map, alerts, hazards, cross-section, vertical
profile, situation panel, messages, execution report, and the
top-level ``AWCIDashboard``/``AWCIDashboardWindow``), moved as a whole
into their own package. This is the blueprint's own
``awci/dashboard/`` "application layer above everything else" -
real module names are kept as-is rather than renamed to the
blueprint's own illustrative file names (``application.py``,
``layout.py``, ...), since the real structure here is already
functional, tested code, not a fresh build.

``acf.gui.dashboard.awci_<x>`` is kept as a real backward-compatible
re-export for every module. Several real ACF-side modules
(``acf.gui.dashboard.acf_workstation_*.py``, ``acf.gui.dashboard.
acf_general_dashboard.py``, ``acf.dashboard.window.py``,
``acf.awci_app.py``) genuinely reuse pieces of this dashboard (most
commonly ``AWCIMapPanel`` as a reusable map widget, or launch
``AWCIDashboardWindow`` directly) - these were deliberately left
importing the ``acf.gui.dashboard.awci_*`` shim rather than repointed
to this package directly, exactly as every other ACF-side caller of a
migrated AWCI module has been left throughout this whole migration;
only already-migrated ``awci.*`` code and this package's own internal
cross-references were repointed to the new, real location.
"""
