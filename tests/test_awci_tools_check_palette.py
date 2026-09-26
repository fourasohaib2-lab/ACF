"""Palette measurement tool: CIEDE2000 against the published test pairs, WCAG contrast, the retained palette."""

import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("check_palette", Path(__file__).parents[1] / "tools" / "awci" / "check_palette.py")
cp = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
spec.loader.exec_module(cp)  # type: ignore[union-attr]


@pytest.mark.parametrize("lab1,lab2,expected", [  # Sharma, Wu & Dalal (2005), Table 1, pairs 1, 7, 17, 25
    ((50.0, 2.6772, -79.7751), (50.0, 0.0, -82.7485), 2.0425),
    ((50.0, 0.0, 0.0), (50.0, -1.0, 2.0), 2.3669),
    ((50.0, 2.5, 0.0), (73.0, 25.0, -18.0), 27.1492),
    ((60.2574, -34.0099, 36.2677), (60.4626, -34.1751, 39.4387), 1.2644),
])
def test_ciede2000_matches_the_published_pairs(lab1: tuple, lab2: tuple, expected: float) -> None:
    assert cp.ciede2000(lab1, lab2) == pytest.approx(expected, abs=1e-4)


def test_wcag_contrast() -> None:
    assert cp.contrast("#ffffff", "#000000") == pytest.approx(21.0)
    assert cp.contrast("#777777", "#777777") == pytest.approx(1.0)


def test_the_retained_vigilance_palette() -> None:
    r = cp.report(["#2e7d32", "#66bb6a", "#ffeb3b", "#ff9100", "#e8413c", "#a52cba"], ["VL", "L", "M", "H", "VH", "EX"])
    assert min(r["contrast"].values()) >= 3.0  # WCAG 1.4.11 on the map surface
    assert r["normal"]["min_all"] >= 20 and r["deutan"]["min_all"] >= 10 and r["tritan"]["min_all"] >= 13
    assert r["protan"]["min_all"] >= 6 and r["protan"]["min_adjacent"] >= 18
