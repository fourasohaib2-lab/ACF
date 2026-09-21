"""Backward-compatible re-export.

Real package moved to ``awci.knowledge`` on 2026-09-21 (Phase 9 of the
AWCI separate-package migration - see ``src/awci/knowledge/__init__.py``'s
own docstring and
``docs/architecture/acf_awci_architecture_gap_analysis.md``). Kept here
so every existing ``acf.aviation`` import keeps working unchanged.
"""

from awci.knowledge import *  # noqa: F401,F403
from awci.knowledge import __all__  # noqa: F401
