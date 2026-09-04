"""
GUI-level tests for
acf.gui.dashboard.acf_workstation_case_study.ACFCaseStudyLabPanel and
its real load_case_studies()/save_case_studies() JSON persistence.
"""

from __future__ import annotations

import json

import pytest
from PySide6.QtWidgets import QApplication, QInputDialog

from acf.gui.dashboard.acf_workstation_case_study import (
    ACFCaseStudyLabPanel,
    load_case_studies,
    save_case_studies,
)


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


# ------------------------------------------------------- persistence


def test_load_case_studies_returns_an_honestly_empty_list_for_a_missing_file(tmp_path):
    path = tmp_path / "does_not_exist.json"
    assert load_case_studies(path) == []


def test_load_case_studies_returns_an_honestly_empty_list_for_malformed_json(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("{ not valid json", encoding="utf-8")
    assert load_case_studies(path) == []


def test_save_then_load_round_trips_a_real_case(tmp_path):
    path = tmp_path / "workstation" / "case_studies.json"
    cases = [{"name": "Test case", "saved_at": "2026-09-04 12:00Z", "config": {"model": "ALADIN"}}]

    save_case_studies(cases, path)

    assert path.exists()
    assert load_case_studies(path) == cases
    assert json.loads(path.read_text(encoding="utf-8")) == cases


# ------------------------------------------------------------- panel


def test_starts_with_the_real_persisted_cases(qapp, tmp_path):
    path = tmp_path / "case_studies.json"
    save_case_studies([{"name": "Existing case", "saved_at": "x", "config": {}}], path)

    panel = ACFCaseStudyLabPanel(export_configuration=lambda: {}, apply_configuration=lambda _c: None, storage_path=path)

    assert panel.case_list.count() == 1
    assert "Existing case" in panel.case_list.item(0).text()


def test_save_current_as_case_calls_export_and_persists(qapp, tmp_path, monkeypatch):
    path = tmp_path / "case_studies.json"
    exported = {"model": "ARPEGE", "level_index": 2}
    monkeypatch.setattr(QInputDialog, "getText", staticmethod(lambda *a, **k: ("My real case", True)))

    panel = ACFCaseStudyLabPanel(export_configuration=lambda: exported, apply_configuration=lambda _c: None, storage_path=path)
    panel._save_current_as_case()

    assert panel.case_list.count() == 1
    assert "My real case" in panel.case_list.item(0).text()
    persisted = load_case_studies(path)
    assert len(persisted) == 1
    assert persisted[0]["name"] == "My real case"
    assert persisted[0]["config"] == exported


def test_save_current_as_case_is_a_no_op_when_the_dialog_is_cancelled(qapp, tmp_path, monkeypatch):
    path = tmp_path / "case_studies.json"
    monkeypatch.setattr(QInputDialog, "getText", staticmethod(lambda *a, **k: ("", False)))

    panel = ACFCaseStudyLabPanel(export_configuration=lambda: {}, apply_configuration=lambda _c: None, storage_path=path)
    panel._save_current_as_case()

    assert panel.case_list.count() == 0
    assert not path.exists()


def test_load_selected_case_calls_apply_configuration_with_the_real_saved_config(qapp, tmp_path):
    path = tmp_path / "case_studies.json"
    save_case_studies([{"name": "Case A", "saved_at": "x", "config": {"model": "AROME"}}], path)
    applied: list[dict] = []

    panel = ACFCaseStudyLabPanel(export_configuration=lambda: {}, apply_configuration=applied.append, storage_path=path)
    panel.case_list.setCurrentRow(0)
    panel._load_selected_case()

    assert applied == [{"model": "AROME"}]
    assert "✅" in panel.status_label.text()


def test_load_selected_case_without_a_selection_reports_an_honest_error(qapp, tmp_path):
    path = tmp_path / "case_studies.json"
    panel = ACFCaseStudyLabPanel(export_configuration=lambda: {}, apply_configuration=lambda _c: None, storage_path=path)

    panel._load_selected_case()

    assert "⚠" in panel.status_label.text()


def test_delete_selected_case_removes_it_from_the_real_list_and_disk(qapp, tmp_path):
    path = tmp_path / "case_studies.json"
    save_case_studies([{"name": "To delete", "saved_at": "x", "config": {}}], path)
    panel = ACFCaseStudyLabPanel(export_configuration=lambda: {}, apply_configuration=lambda _c: None, storage_path=path)
    panel.case_list.setCurrentRow(0)

    panel._delete_selected_case()

    assert panel.case_list.count() == 0
    assert load_case_studies(path) == []


def test_update_from_volume_is_a_real_no_op(qapp, tmp_path):
    """Real regression guard: this panel must never crash when
    ACFWorkstation._render_all_panels() calls it uniformly, even
    though it manages settings, not volume data."""
    path = tmp_path / "case_studies.json"
    panel = ACFCaseStudyLabPanel(export_configuration=lambda: {}, apply_configuration=lambda _c: None, storage_path=path)

    panel.update_from_volume({"n_levels": 5}, level_index=2)  # must not raise
