"""Backward-compatible re-export.

Real module moved to ``awci.dashboard.awci_stats_bar`` on 2026-09-21
(Phase 10 of the AWCI separate-package migration - see
``src/awci/dashboard/__init__.py``'s own docstring and
``docs/architecture/acf_awci_architecture_gap_analysis.md``). Kept
here so every existing ``acf.gui.dashboard.awci_stats_bar`` import keeps
working unchanged.
"""

from awci.dashboard.awci_stats_bar import *  # noqa: F401,F403
