"""Backward-compatible re-export.

Real module moved to ``awci.data.model_import_cross_section`` on
2026-09-21 (Phase 8 of the AWCI separate-package migration - see
``src/awci/data/__init__.py``'s own docstring and
``docs/architecture/acf_awci_architecture_gap_analysis.md``). Kept
here so every existing ``acf.awci.model_import_cross_section`` import
keeps working unchanged.
"""

from awci.data.model_import_cross_section import *  # noqa: F401,F403
