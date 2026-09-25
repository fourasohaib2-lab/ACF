"""Backward-compatible re-export.

Real module moved to ``awci.data.archive_field`` on 2026-09-21
(Phase 4 of the AWCI separate-package migration - see
``src/awci/data/__init__.py``'s own docstring and
``docs/architecture/acf_awci_architecture_gap_analysis.md``). Kept
here so every existing ``acf.awci.archive_field`` import keeps
working unchanged.
"""

from awci.data.archive_field import *  # noqa: F401,F403
