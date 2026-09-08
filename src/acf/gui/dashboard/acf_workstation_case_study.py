"""
ACF Scientific Workstation — Case Study Lab
==============================================

Real, named library of reproducible Workstation CONFIGURATIONS for
`acf_workstation.ACFWorkstation` (see that module's own docstring for
the Workstation's overall "ACF CORE ONLY - NO AWCI" rule).

Honest reinterpretation of "Case Study Lab" - why, not fabricated data
-------------------------------------------------------------------------
The master spec's own "Case Study Lab" naming could be read as a
library of real HISTORICAL weather events (e.g. "Storm X, 12 March
2024") - this codebase has no real archived operational NWP/observation
data anywhere (confirmed repeatedly throughout this Workstation's own
build - `CoupledEarthSolver` always stands in for a real operational
model, never a real archive; see e.g. `ModelConsensusEngine.
compute_real_multi_model_disagreement()`'s own honest_limitation).
Building a library of named "historical cases" from that would mean
either fabricating events that never happened or mislabeling live
solver output as archived fact - exactly what this project's audits
exist to catch.

The real, honest interpretation built here instead: a "case" is a real,
named, reproducible Workstation CONFIGURATION (model, level, nav, every
Lab's own variable selector - reusing `ACFWorkstation._export_
configuration()`/`_apply_configuration()` from Configuration Management,
added 2026-09-04) the user has bookmarked because it was interesting to
set up and look at again - e.g. "Wind shear vs relative humidity view"
or "ARPEGE θ-e at level 3" - never a claim that a specific real weather
event is being replayed. Same "settings, never data" principle
Configuration Management already established: loading a case still
requires pressing "🔄 Run" for real, fresh data.

Real, durable local storage
-------------------------------
Saved as a real JSON file under `<repo_root>/data/workstation/
case_studies.json` - same real `<repo_root>/data/*` convention already
established by `acf.web.routers.events_router`/`datasets_router`'s own
`DEFAULT_*_DB_PATH`. A missing or malformed file is treated as an
honestly-empty real library (never a fatal crash on first use, or on a
corrupted/hand-edited file).
"""

from __future__ import annotations

import json
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PySide6.QtWidgets import (
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from acf.gui.theme_tokens import label_style

#: Same real `<repo_root>/data/*` convention already established by
#: acf.web.routers.events_router.DEFAULT_EVENT_DB_PATH/
#: datasets_router.DEFAULT_DATASET_DB_PATH.
DEFAULT_CASE_STUDY_PATH = Path(__file__).resolve().parents[4] / "data" / "workstation" / "case_studies.json"


def load_case_studies(path: Path = DEFAULT_CASE_STUDY_PATH) -> list[dict[str, Any]]:
    """Real, defensive load - a missing file is an honestly-empty real
    library (first use); a malformed/corrupted file (hand-edited, or
    from an incompatible future format) is also treated as empty
    rather than crashing the whole panel on open."""
    if not path.exists():
        return []
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return []
    return data if isinstance(data, list) else []


def save_case_studies(cases: list[dict[str, Any]], path: Path = DEFAULT_CASE_STUDY_PATH) -> None:
    """Real, durable write - creates `<repo_root>/data/workstation/`
    if this is the real first case ever saved."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(cases, handle, indent=2)


class ACFCaseStudyLabPanel(QWidget):
    """Real Case Study Lab - a named library of real, reproducible
    Workstation configurations. No AWCI content, no fabricated
    historical events anywhere - see module docstring."""

    def __init__(
        self,
        export_configuration: Callable[[], dict[str, Any]],
        apply_configuration: Callable[[dict[str, Any]], None],
        storage_path: Path = DEFAULT_CASE_STUDY_PATH,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._export_configuration = export_configuration
        self._apply_configuration = apply_configuration
        self._storage_path = storage_path
        self._cases: list[dict[str, Any]] = load_case_studies(storage_path)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        layout.addWidget(
            self._header(
                "CASE STUDY LAB — a real, named library of reproducible Workstation configurations "
                "(settings only, never a snapshot of computed data - press \"🔄 Run\" after loading a case)"
            )
        )

        save_row = QHBoxLayout()
        self.save_button = QPushButton("💾 Save Current Configuration as Case…")
        self.save_button.setToolTip(
            "Real acf_workstation.ACFWorkstation._export_configuration() - saves the current\n"
            "real model/level/nav/every Lab's own selector, under a real name you choose."
        )
        self.save_button.clicked.connect(self._save_current_as_case)
        save_row.addWidget(self.save_button)
        save_row.addStretch()
        layout.addLayout(save_row)

        self.case_list = QListWidget()
        for case in self._cases:
            self.case_list.addItem(self._list_item_text(case))
        layout.addWidget(self.case_list, stretch=1)

        actions_row = QHBoxLayout()
        self.load_button = QPushButton("📂 Load Selected Case")
        self.load_button.clicked.connect(self._load_selected_case)
        actions_row.addWidget(self.load_button)
        self.delete_button = QPushButton("🗑 Delete Selected Case")
        self.delete_button.clicked.connect(self._delete_selected_case)
        actions_row.addWidget(self.delete_button)
        actions_row.addStretch()
        layout.addLayout(actions_row)

        self.status_label = QLabel("—")
        self.status_label.setStyleSheet(label_style("text_muted", "xs"))
        layout.addWidget(self.status_label)

    @staticmethod
    def _header(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(label_style("text_secondary", "xs", "bold"))
        lbl.setWordWrap(True)
        return lbl

    @staticmethod
    def _list_item_text(case: dict[str, Any]) -> str:
        name = case.get("name", "(unnamed)")
        saved_at = case.get("saved_at", "")
        model = case.get("config", {}).get("model", "")
        return f"{name} — {model} — saved {saved_at}"

    def update_from_volume(self, volume: dict[str, Any], level_index: int) -> None:
        """Real no-op - this panel manages real saved SETTINGS, never
        the current volume's own data (same uniform per-panel
        `update_from_volume()` signature every other Lab panel uses,
        kept here only so `ACFWorkstation._render_all_panels()` never
        needs to special-case this panel)."""

    # ------------------------------------------------------------ actions

    def _save_current_as_case(self) -> None:
        name, accepted = QInputDialog.getText(self, "Save Case", "Real, reproducible case name:")
        if not accepted or not name.strip():
            return
        config = self._export_configuration()
        case = {
            "name": name.strip(),
            "saved_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M") + "Z",
            "config": config,
        }
        self._cases.append(case)
        save_case_studies(self._cases, self._storage_path)
        self.case_list.addItem(self._list_item_text(case))
        self.status_label.setText(f"✅ Case '{case['name']}' saved.")

    def _load_selected_case(self) -> None:
        row = self.case_list.currentRow()
        if row < 0 or row >= len(self._cases):
            self.status_label.setText("⚠ Select a case to load first.")
            return
        case = self._cases[row]
        self._apply_configuration(case.get("config", {}))
        self.status_label.setText(f"✅ Case '{case.get('name', '')}' loaded - press \"🔄 Run\" for real data.")

    def _delete_selected_case(self) -> None:
        row = self.case_list.currentRow()
        if row < 0 or row >= len(self._cases):
            self.status_label.setText("⚠ Select a case to delete first.")
            return
        case = self._cases.pop(row)
        save_case_studies(self._cases, self._storage_path)
        self.case_list.takeItem(row)
        self.status_label.setText(f"🗑 Case '{case.get('name', '')}' deleted.")
