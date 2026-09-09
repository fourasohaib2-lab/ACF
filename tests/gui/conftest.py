"""
GUI-suite pytest configuration.

Historical note (2026-09-09): per-test pyplot figure cleanup and the
headless `QT_QPA_PLATFORM=offscreen` default both live in the ROOT
`tests/conftest.py` now, so they also cover the AWCI panel tests at
`tests/` root (test_awci_map_panel_no_mtg.py, the ESOC field tests, …)
and are in effect before the FIRST QApplication of the session is
constructed (the Qt platform binds at that moment, not per-test). This
file is kept as the GUI-suite's configuration anchor for any future
GUI-only fixtures.
"""

from __future__ import annotations
