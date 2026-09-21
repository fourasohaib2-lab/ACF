"""Backward-compatible re-export.

Real module moved to ``awci.comparison.multi_model_fusion`` on
2026-09-21 (Phase 8 of the AWCI separate-package migration - see
``src/awci/comparison/__init__.py``'s own docstring and
``docs/architecture/acf_awci_architecture_gap_analysis.md``). Kept
here so every existing ``acf.awci.multi_model_fusion`` import keeps
working unchanged.
"""

from awci.comparison.multi_model_fusion import *  # noqa: F401,F403
