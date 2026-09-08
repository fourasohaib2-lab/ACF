"""
Tests for AWCIMapPanel's real multi-format export menu (PNG/SVG/CSV/
JSON, added 2026-09-04) - the download_button became a real QToolButton
+ QMenu (same "real actions behind one control" convention already
established for ACFGeneralDashboard's own "☰" menu), replacing the
previous PNG-only QPushButton. Every existing real caller/test only
ever checked `panel.download_button is not None` - never its exact Qt
type - so this is a real, backward-compatible extension.
"""

from __future__ import annotations

import csv
import json

from PySide6.QtWidgets import QFileDialog, QMenu, QToolButton

from acf.gui.dashboard.awci_map_panel import AWCIMapPanel


def test_download_button_is_a_real_tool_button_with_a_real_export_menu(qtbot):
    panel = AWCIMapPanel("AWCI GLOBAL MAP")
    qtbot.addWidget(panel)

    assert isinstance(panel.download_button, QToolButton)
    menu = panel.download_button.menu()
    assert isinstance(menu, QMenu)
    action_texts = [a.text() for a in menu.actions() if not a.isSeparator()]
    assert action_texts == ["Save as PNG…", "Save as SVG…", "Export data as CSV…", "Export data as JSON…"]


def test_export_png_writes_a_real_file(qtbot, tmp_path, monkeypatch):
    panel = AWCIMapPanel("AWCI GLOBAL MAP")
    qtbot.addWidget(panel)
    target = tmp_path / "map.png"
    monkeypatch.setattr(QFileDialog, "getSaveFileName", staticmethod(lambda *a, **k: (str(target), "")))

    panel._export_png()

    assert target.exists()
    assert target.stat().st_size > 0


def test_export_svg_writes_a_real_vector_file(qtbot, tmp_path, monkeypatch):
    panel = AWCIMapPanel("AWCI GLOBAL MAP")
    qtbot.addWidget(panel)
    target = tmp_path / "map.svg"
    monkeypatch.setattr(QFileDialog, "getSaveFileName", staticmethod(lambda *a, **k: (str(target), "")))

    panel._export_svg()

    assert target.exists()
    content = target.read_text(encoding="utf-8")
    assert "<svg" in content  # a real SVG document, not a renamed PNG


def test_export_cancel_writes_no_file(qtbot, tmp_path, monkeypatch):
    panel = AWCIMapPanel("AWCI GLOBAL MAP")
    qtbot.addWidget(panel)
    target = tmp_path / "cancelled.png"
    monkeypatch.setattr(QFileDialog, "getSaveFileName", staticmethod(lambda *a, **k: ("", "")))

    panel._export_png()

    assert not target.exists()


def test_export_csv_matches_the_real_currently_rendered_grid(qtbot, tmp_path, monkeypatch):
    panel = AWCIMapPanel("AWCI GLOBAL MAP")
    qtbot.addWidget(panel)  # __init__ already ran update_data() once - real data is available
    target = tmp_path / "data.csv"
    monkeypatch.setattr(QFileDialog, "getSaveFileName", staticmethod(lambda *a, **k: (str(target), "")))

    panel._export_csv()

    assert target.exists()
    with open(target, newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    assert rows[0] == ["lat", "lon", "value"]
    n_lats, n_lons = len(panel._last_lats), len(panel._last_lons)
    assert len(rows) == 1 + n_lats * n_lons  # header + one real row per real grid cell
    # A real, in-range AWCI value (0-100 scale) round-trips through the CSV.
    first_data_row = rows[1]
    assert float(first_data_row[0]) == float(panel._last_lats[0])
    assert float(first_data_row[1]) == float(panel._last_lons[0])
    assert 0.0 <= float(first_data_row[2]) <= 100.0


def test_export_json_matches_the_real_currently_rendered_grid(qtbot, tmp_path, monkeypatch):
    panel = AWCIMapPanel("AWCI GLOBAL MAP")
    qtbot.addWidget(panel)
    target = tmp_path / "data.json"
    monkeypatch.setattr(QFileDialog, "getSaveFileName", staticmethod(lambda *a, **k: (str(target), "")))

    panel._export_json()

    assert target.exists()
    payload = json.loads(target.read_text(encoding="utf-8"))
    assert payload["title"] == panel._title
    assert payload["exported_at"].endswith("Z")  # real wall-clock UTC, not a fabricated forecast time
    assert len(payload["lats"]) == len(panel._last_lats)
    assert len(payload["lons"]) == len(panel._last_lons)
    assert len(payload["grid"]) == len(panel._last_lats)
    assert len(payload["grid"][0]) == len(panel._last_lons)


def test_export_honestly_writes_nan_cells_as_empty_csv_and_null_json(qtbot, tmp_path, monkeypatch):
    """Real regression guard: a genuinely blank cell (this panel's own
    show_demo_fallback=False empty state) must never be exported as a
    fabricated 0."""
    panel = AWCIMapPanel("WORKSTATION PANEL", show_demo_fallback=False)
    qtbot.addWidget(panel)  # no set_external_field() call -> the whole grid is honestly NaN

    csv_target = tmp_path / "blank.csv"
    monkeypatch.setattr(QFileDialog, "getSaveFileName", staticmethod(lambda *a, **k: (str(csv_target), "")))
    panel._export_csv()
    with open(csv_target, newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    assert rows[1][2] == ""  # empty, not "0" or "0.0"

    json_target = tmp_path / "blank.json"
    monkeypatch.setattr(QFileDialog, "getSaveFileName", staticmethod(lambda *a, **k: (str(json_target), "")))
    panel._export_json()
    payload = json.loads(json_target.read_text(encoding="utf-8"))
    assert payload["grid"][0][0] is None
    assert all(value is None for row in payload["grid"] for value in row)


def test_export_csv_and_json_are_no_ops_before_any_real_data_exists():
    """A real, honest edge case (not reachable via the normal
    constructor, which already calls update_data() once) - both export
    methods must not crash on a genuinely absent _last_grid."""
    panel = AWCIMapPanel.__new__(AWCIMapPanel)
    panel._last_grid = None
    panel._last_lats = None
    panel._last_lons = None

    panel._export_csv()  # must return early, not raise
    panel._export_json()


def test_default_export_stem_matches_the_panels_own_title():
    stem = AWCIMapPanel.__dict__["_default_export_stem"]

    class _Stub:
        _base_title = "AWCI Regional Map"

    assert stem(_Stub()) == "awci_regional_map"
