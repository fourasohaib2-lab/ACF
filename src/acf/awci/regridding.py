"""Backward-compatible re-export.

Real module moved to ``awci.comparison.regridding`` on 2026-09-21
(Phase 8 of the AWCI separate-package migration - see
``src/awci/comparison/__init__.py``'s own docstring and
``docs/architecture/acf_awci_architecture_gap_analysis.md``). Kept
here so every existing ``acf.awci.regridding`` import keeps working
unchanged.
"""

from awci.comparison.regridding import *  # noqa: F401,F403

# `import *` above never re-exports underscore-prefixed names by design;
# tests/test_regridding.py explicitly imports these two internal helpers
# by name (real, deliberate whitebox tests of the conservative-regridding
# edge/weight math), so they need an explicit re-export here too.
from awci.comparison.regridding import _cell_edges_latitude, _natural_edges  # noqa: F401
