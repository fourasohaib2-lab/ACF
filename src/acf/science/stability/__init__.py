"""
Atmospheric Complexity Framework (ACF)

Atmospheric Stability Science Package

Migrated 2026-09-21 (Phase 2 of the ACF science/ per-domain
reorganization - see
docs/architecture/acf_awci_architecture_gap_analysis.md's own §4
section) from 7 flat modules directly under ``acf.science`` into this
subpackage, matching the blueprint's own ``science/stability/`` layer.
Real module names kept as-is. ``acf.science.<module>`` is kept as a
real backward-compatible re-export for every one of them.

``stability.py``'s own ``Stability`` class is a real composite index
aggregator spanning both this package and ``science.convection`` (it
reuses ``CAPE``/``CIN``/``LCL``/``StormRelativeHelicity`` directly) -
a genuine, disclosed cross-package dependency, not a migration
artifact.
"""

from acf.science.stability.bulk_richardson_number import BulkRichardsonNumber
from acf.science.stability.k_index import KIndex
from acf.science.stability.lifted_index import LiftedIndex
from acf.science.stability.showalter_index import ShowalterIndex
from acf.science.stability.stability import Stability
from acf.science.stability.sweat_index import SWEATIndex
from acf.science.stability.total_totals import TotalTotals

__all__ = [
    "BulkRichardsonNumber",
    "KIndex",
    "LiftedIndex",
    "SWEATIndex",
    "ShowalterIndex",
    "Stability",
    "TotalTotals",
]
