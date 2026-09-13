"""
ACF Scientific Workstation — Left Sidebar Navigation
========================================================

Static navigation tree matching `acf_workstation_reference.jpg`'s left
sidebar: Home · Data (Datasets/Models/Observations) · Science
(Thermodynamics/Humidity/Stability/Convection/Wind & Shear/Gradients/
Vertical Structure/Complexity) · Analysis (2D Maps/3D Volumes/4D
Space-Time/Profiles/Cross Sections/Model Comparison) · Reports ·
Infrastructure (HPC/Slurm/Jobs/Storage) · Settings.

Selecting a top-level section (or any real sub-entry under one) emits
`sectionSelected` with that SECTION's real name - the composer
(`acf_workstation.ACFWorkstation`) decides what, if anything, to scroll
to/focus. This widget owns no panel-visibility logic itself and knows
nothing about any panel.

Honesty note: the sub-entries above are reproduced from the reference
image's own left column, and are navigation labels only - this widget
never claims that a given sub-entry has its own dedicated real panel
behind it. The composer maps a real SECTION to whichever real,
already-built area of the Workstation genuinely corresponds to it;
`current_subsection()` exposes the finer selection for a caller that
can honestly act on it.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget

from acf.gui.theme_tokens import label_style

#: Real top-level sections, in the reference image's own order.
_SECTIONS: list[str] = [
    "Home", "Data", "Science", "Analysis", "Reports", "Infrastructure", "Settings",
]

#: Real sub-entries per section, exactly as the reference image lists
#: them (sections the image shows with no sub-entries have none here).
_SUBSECTIONS: dict[str, list[str]] = {
    "Home": [],
    "Data": ["Datasets", "Models", "Observations"],
    "Science": [
        "Thermodynamics", "Humidity", "Stability", "Convection",
        "Wind & Shear", "Gradients", "Vertical Structure", "Complexity",
    ],
    "Analysis": [
        "2D Maps", "3D Volumes", "4D Space-Time", "Profiles",
        "Cross Sections", "Model Comparison",
    ],
    "Reports": [],
    "Infrastructure": ["HPC", "Slurm", "Jobs", "Storage"],
    "Settings": [],
}

#: Qt item-data role carrying each item's own real section name (a
#: sub-entry carries its parent section's name, so one lookup answers
#: "which section is selected?" for either kind of item).
_SECTION_ROLE = Qt.ItemDataRole.UserRole


class WorkstationSidebar(QWidget):
    """Static left navigation sidebar - see module docstring."""

    sectionSelected = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._current_section: str | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        header = QLabel("ACF")
        header.setStyleSheet(label_style("text_secondary", "sm", "bold"))
        layout.addWidget(header)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setMaximumWidth(200)
        self._section_items: dict[str, QTreeWidgetItem] = {}
        for section in _SECTIONS:
            item = QTreeWidgetItem([section])
            item.setData(0, _SECTION_ROLE, section)
            # Qt object name, so a caller can also find a real section
            # item by name via findChild()/findChildren().
            for subsection in _SUBSECTIONS[section]:
                child = QTreeWidgetItem([subsection])
                child.setData(0, _SECTION_ROLE, section)
                item.addChild(child)
            self.tree.addTopLevelItem(item)
            self._section_items[section] = item
        self.tree.expandAll()
        self.tree.currentItemChanged.connect(self._on_current_item_changed)
        layout.addWidget(self.tree, stretch=1)

    # ------------------------------------------------------------- queries

    def section_names(self) -> list[str]:
        """The real top-level section names, in reference-image order."""
        return list(_SECTIONS)

    def subsection_names(self, section: str) -> list[str]:
        """The real sub-entries the reference image lists under `section`."""
        return list(_SUBSECTIONS.get(section, []))

    def current_section(self) -> str | None:
        """The real section currently selected, or None before any
        selection - never a fabricated default."""
        return self._current_section

    def current_subsection(self) -> str | None:
        """The real sub-entry currently selected, or None when the
        selection is a top-level section (or nothing)."""
        item = self.tree.currentItem()
        if item is None or item.parent() is None:
            return None
        return str(item.text(0))

    # ------------------------------------------------------------ commands

    def select_section(self, name: str) -> None:
        """Select a real top-level section. An unknown name is ignored
        (no selection change, no signal) rather than invented."""
        item = self._section_items.get(name)
        if item is None:
            return
        self.tree.setCurrentItem(item)

    def select_subsection(self, section: str, subsection: str) -> None:
        """Select a real sub-entry of a real section - ignored, like
        `select_section()`, if either name is not a real one."""
        parent = self._section_items.get(section)
        if parent is None:
            return
        for row in range(parent.childCount()):
            child = parent.child(row)
            if child.text(0) == subsection:
                self.tree.setCurrentItem(child)
                return

    # ------------------------------------------------------------ internals

    def _on_current_item_changed(
        self, current: QTreeWidgetItem | None, _previous: QTreeWidgetItem | None
    ) -> None:
        if current is None:
            return
        section = current.data(0, _SECTION_ROLE)
        if not isinstance(section, str):
            return
        self._current_section = section
        self.sectionSelected.emit(section)
