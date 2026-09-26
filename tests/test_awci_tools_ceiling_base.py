"""Ceiling-base variants of tools/awci/evaluate_ceiling_base.py (evidence cited in AWCI_WEB_SP3.md)."""

import importlib.util
from pathlib import Path

import numpy as np
import pytest

spec = importlib.util.spec_from_file_location("ecb", Path(__file__).parents[1] / "tools" / "awci" / "evaluate_ceiling_base.py")
ecb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ecb)

GH = np.array([110.0, 760.0, 1450.0, 3000.0])  # 1000, 925, 850, 700 hPa over a sea-level station


def test_level_variant_keeps_the_diagnosis() -> None:
    assert ecb.refined_ceiling_m(110.0, GH, 0.0, 240.0, "level") == 110.0


def test_lcl_inside_the_level_interval_becomes_the_base() -> None:
    # 1000 hPa level represents 0 .. (110+760)/2 = 435 m: an LCL of 240 m lies inside
    assert ecb.refined_ceiling_m(110.0, GH, 0.0, 240.0, "lcl_in_level") == pytest.approx(240.0)
    assert ecb.refined_ceiling_m(110.0, GH, 0.0, 900.0, "lcl_in_level") == pytest.approx(110.0)  # outside: kept
    assert ecb.refined_ceiling_m(110.0, GH, 0.0, 900.0, "lcl_clip") == pytest.approx(435.0)


def test_no_ceiling_stays_none() -> None:
    assert np.isnan(ecb.refined_ceiling_m(np.nan, GH, 0.0, 240.0, "lcl_in_level"))
