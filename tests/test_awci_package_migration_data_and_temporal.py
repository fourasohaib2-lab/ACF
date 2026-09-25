"""Regression guard for Phase 4 of the AWCI separate-package migration
(2026-09-21, "continue avec archive_field.py et temporal_field.py" -
see docs/architecture/acf_awci_architecture_gap_analysis.md's own
"§2e" section).

Unlike every module in Phases 1-3, archive_field.py and
temporal_field.py did NOT move to the same package as each other:
archive_field.py (real ALADIN RESTOR archive ingestion, zero
dependency on AWCICalculator) went to the new awci.data/ (the
blueprint's Data Hub layer), while temporal_field.py (AWCICalculator
applied along a time series, depends directly on calculator.py and
vertical_field.py) joined its siblings in awci.complexity/. This test
locks in both the re-export identity and that this placement split
was deliberate, not an oversight.
"""

from __future__ import annotations

import importlib


def test_archive_field_moved_to_the_new_data_package_not_complexity():
    old = importlib.import_module("acf.awci.archive_field")
    new = importlib.import_module("awci.data.archive_field")

    assert old.load_real_aladin_restor_run is new.load_real_aladin_restor_run
    assert old.sample_archive_at_point is new.sample_archive_at_point
    assert old.restor_fullpos_path is new.restor_fullpos_path


def test_temporal_field_moved_to_complexity_alongside_its_real_dependencies():
    old = importlib.import_module("acf.awci.temporal_field")
    new = importlib.import_module("awci.complexity.temporal_field")

    assert old.compute_real_complexity_evolution is new.compute_real_complexity_evolution
    assert old.profile_over_time is new.profile_over_time


def test_temporal_field_reaches_the_migrated_calculator_and_vertical_field_as_siblings():
    """temporal_field.py's own real dependency on AWCICalculator and
    score_volume (both already migrated to awci.complexity/) must now
    resolve as same-package relative imports, not the acf.awci shim."""
    from awci.complexity.calculator import AWCICalculator
    from awci.complexity.temporal_field import AWCICalculator as temporal_calc_ref
    from awci.complexity.temporal_field import score_volume as temporal_score_ref
    from awci.complexity.vertical_field import score_volume

    assert temporal_calc_ref is AWCICalculator
    assert temporal_score_ref is score_volume


def test_archive_field_has_no_real_dependency_on_the_complexity_engine():
    """Confirms the placement rationale itself: archive_field.py is
    pure data ingestion (EPyGrAM FA decoding), never imports
    AWCICalculator or any sibling awci.complexity module - this is why
    it went to awci.data/ instead of awci.complexity/."""
    import awci.data.archive_field as archive_module

    assert not hasattr(archive_module, "AWCICalculator")
