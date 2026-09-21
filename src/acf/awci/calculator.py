"""Backward-compatible re-export.

Real module moved to ``awci.complexity.calculator`` on 2026-09-21
(Phase 2 of the AWCI separate-package migration - see
``src/awci/complexity/__init__.py``'s own docstring and
``docs/architecture/acf_awci_architecture_gap_analysis.md``). Kept
here so every existing ``acf.awci.calculator`` import - by far this
package's most widely-depended-on module before this migration -
keeps working unchanged.
"""

from awci.complexity.calculator import *  # noqa: F401,F403
