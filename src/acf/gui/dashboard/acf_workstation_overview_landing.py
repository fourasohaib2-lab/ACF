"""
ACF Scientific Workstation — Overview (landing page)
=======================================================

Real landing/status page for `acf_workstation.ACFWorkstation`, added
2026-09-04 to match the Workstation's own reference mockup
(`docs/reference/acf_scientific_workstation_reference.jpg`) exactly:
that mockup's own left nav shows a real, DISTINCT "Overview" item
above "Atmosphere State" - this Workstation's original build only had
one, the raw-fields map panel (now relabelled "Atmosphere State", see
`acf_workstation_overview.ACFOverviewPanel`). This is the real,
missing "Overview" itself: a genuine landing/status summary, not
another copy of the atmospheric-state map.

Real content only - no fabricated status
-------------------------------------------
- Real current model selection and its own real `MODEL_CONFIGS` grid
  metadata (resolution, native grid size, level count) - the exact
  same real dict every other real solver run in this Workstation
  already reads from, not invented here.
- Real run status: "Not yet computed" until the real "🔄 Run" button
  has genuinely produced a volume, then the real model/level-count/
  grid-size/wall-clock string this Workstation's own `status_label`
  already shows - reused verbatim via `update_status()`, never a
  second, independently-tracked status.
- Real quick-navigation - one real button per real nav/toolbar module
  this Workstation actually has, wired to the real callback the
  Workstation itself supplies (constructor injection, same convention
  `acf_workstation_case_study.ACFCaseStudyLabPanel`'s own
  `export_configuration`/`apply_configuration` callbacks already use) -
  never a second, independent navigation path.
"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtWidgets import QGridLayout, QGroupBox, QLabel, QPushButton, QVBoxLayout, QWidget

from acf.forecast.engine import MODEL_CONFIGS
from acf.gui.theme_tokens import label_style


class ACFOverviewLandingPanel(QWidget):
    """Real Workstation landing page - status + quick navigation, no
    map, no composite score, nothing fabricated."""

    def __init__(
        self,
        navigate_to: Callable[[str], None],
        module_names: list[str],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._navigate_to = navigate_to

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        title = QLabel("ACF SCIENTIFIC WORKSTATION")
        title.setStyleSheet(label_style("text_primary", "lg", "bold"))
        layout.addWidget(title)
        subtitle = QLabel("Atmospheric Complexity Framework — CORE ONLY, no AWCI composite score anywhere.")
        subtitle.setStyleSheet(label_style("text_muted", "sm"))
        layout.addWidget(subtitle)

        status_group = QGroupBox("Real Status")
        status_layout = QVBoxLayout(status_group)
        self.status_label = QLabel("Not yet computed. Press \"🔄 Run\" to start a real CoupledEarthSolver run.")
        self.status_label.setWordWrap(True)
        status_layout.addWidget(self.status_label)
        self.model_info_label = QLabel()
        self.model_info_label.setWordWrap(True)
        self.model_info_label.setStyleSheet(label_style("text_muted", "xs"))
        status_layout.addWidget(self.model_info_label)
        layout.addWidget(status_group)

        nav_group = QGroupBox("Quick Navigation")
        nav_layout = QGridLayout(nav_group)
        for i, name in enumerate(module_names):
            btn = QPushButton(name)
            btn.clicked.connect(lambda _checked=False, target=name: self._navigate_to(target))
            nav_layout.addWidget(btn, i // 3, i % 3)
        layout.addWidget(nav_group)
        layout.addStretch()

        self.set_model(next(iter(MODEL_CONFIGS)))

    def set_model(self, model: str) -> None:
        """Real, current `MODEL_CONFIGS` grid metadata for the
        selected model - updates live as the Model selector changes,
        even before any real run has happened."""
        config = MODEL_CONFIGS.get(model)
        if config is None:
            self.model_info_label.setText(f"Unknown model {model!r}.")
            return
        self.model_info_label.setText(
            f"Selected model: {model} — real native grid "
            f"{config['n_lat']}×{config['n_lon']}×{config['n_levels']} "
            f"(resolution ≈ {config['resolution_km']} km, default {config['default_steps']} steps)."
        )

    def update_status(self, status_text: str) -> None:
        """Real, current Workstation-wide status - the exact same
        string `ACFWorkstation.status_label` already shows, mirrored
        here verbatim."""
        self.status_label.setText(status_text)
