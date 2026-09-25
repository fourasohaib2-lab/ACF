"""Backward-compatible re-export.

Real module moved to ``awci.complexity.normalizer`` on 2026-09-21
(Phase 2 of the AWCI separate-package migration - see
``src/awci/complexity/__init__.py``'s own docstring and
``docs/architecture/acf_awci_architecture_gap_analysis.md``). Kept
here so every existing ``acf.awci.normalizer`` import keeps working
unchanged - including the already-migrated
``awci.hazards.microburst``, which still reaches this real class via
``acf.awci.normalizer``.
"""

from awci.complexity.normalizer import *  # noqa: F401,F403
