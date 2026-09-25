"""Backward-compatible re-export.

Real module moved to ``awci.dashboard.awci_dashboard`` on 2026-09-21
(Phase 10 of the AWCI separate-package migration - see
``src/awci/dashboard/__init__.py``'s own docstring and
``docs/architecture/acf_awci_architecture_gap_analysis.md``). Kept
here so every existing ``acf.gui.dashboard.awci_dashboard`` import keeps
working unchanged.
"""

from awci.dashboard.awci_dashboard import *  # noqa: F401,F403

# `import *` above never re-exports underscore-prefixed names by design;
# real whitebox tests import these directly, so they need an explicit
# re-export here too.
from awci.dashboard.awci_dashboard import _FLIGHT_LEVEL_SELECTOR_OPTIONS_HPA, _POINT_OF_INTEREST, _ALL_VERTICAL_PROFILE_LEVELS_HPA, _AIRPORTS, _REGIONAL_ROUTE, _ModelConsensusWorker, _REGIONAL_CITY_LABELS, _ModelDisagreementFieldWorker, _ModelVerticalProfilesWorker  # noqa: F401
