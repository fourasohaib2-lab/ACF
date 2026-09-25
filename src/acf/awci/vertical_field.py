"""Backward-compatible re-export.

Real module moved to ``awci.complexity.vertical_field`` on 2026-09-21
(Phase 3 of the AWCI separate-package migration - see
``src/awci/complexity/__init__.py``'s own docstring and
``docs/architecture/acf_awci_architecture_gap_analysis.md``). Kept
here so every existing ``acf.awci.vertical_field`` import keeps
working unchanged.
"""

from awci.complexity.vertical_field import *  # noqa: F401,F403
