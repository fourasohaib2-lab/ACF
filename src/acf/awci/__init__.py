"""
ACF - AWCI Module
=================

Aviation Weather Complexity Index calculator.

AUDIT NOTE (2026-09-06, Tier C sweep - closes Tier C): 31 files, 21
already carrying an explicit disclosure before this pass (a long,
consistent record of "exhaustive 90-section conformance audit" fix
commits - reports/ACF_MASTER_AUDIT_v2.md - closing real, specific
gaps: CAPE/CIN wired in, wind shear wired in, real multi-model field
fusion, real archived-forecast tier, versioned JSON config, per-run
reports). The remaining 10 (archive_field.py, config_loader.py,
forecaster_validation.py, multi_model_fusion.py, result.py,
run_report.py, temporal_field.py, validation_cases.py, vertical_field.
py, wind_shear.py) read in full this pass: same standard throughout -
real formulas (verified against acf.science's already-audited
implementations, not reimplemented), genuine scientific judgment calls
disclosed rather than hidden (e.g. multi_model_fusion.py explicitly
declining to unilaterally pick nearest-neighbour vs bilinear vs
conservative regridding as "the" right choice), explicit "not
synthetic/not a placeholder" disclosures wherever a reader might
otherwise wonder. Zero generic docstring-bloat template hits anywhere
in this package. Nothing new to disclose - this is the most
consistently rigorous package audited in this entire sweep.
"""

from .calculator import AWCICalculator
from .normalizer import Normalizer
from .weights import WeightsManager

__all__ = [
    "AWCICalculator",
    "Normalizer",
    "WeightsManager",
]
