"""
AWCI Component Detail
======================

Real, per-module detail for the "AWCI COMPONENTS" panel - explicit
user request "rend les bouton des différents complexité utilisable
pour rendre tout le details de la situation" (make the complexity
component buttons usable, to show the full detail of the situation).

Every fact in COMPONENT_INFO below is transcribed directly from
acf.awci.calculator.AWCICalculator.calculate_module_scores() and
acf.awci.normalizer.Normalizer - the real formula/range/blend weight
each module actually uses, not re-derived or guessed.

Honest real-vs-default disclosure: in "🔬 Real Physics" mode today,
acf.awci.vertical_field.compute_real_complexity_volume() only supplies
temperature/wind_speed/specific_humidity/pressure (its own docstring
says so) - convective/microphysical/topographic/temporal/confidence
are pinned at AWCICalculator's own defaults (0.0 contribution / 100%
confidence), NOT genuinely computed from real physics. The demo
synthetic pattern (acf.gui.dashboard.awci_synthetic_field) does supply
all 7 real-shaped inputs, so every module is at least "real" in the
sense of being genuinely computed from *some* real per-point input -
just not always a real Real-Physics-solver-driven one. This module
never claims a pinned default is a real physics-driven result.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout, QWidget

from acf.gui.theme_tokens import TOKENS, dashboard_stylesheet, label_style

Mode = Literal["demo", "real_physics"]


@dataclass(frozen=True)
class ComponentInfo:
    key: str
    icon: str
    label: str
    description: str
    formula: str
    real_inputs: tuple[str, ...]  # real acf.awci.calculator data-dict keys this module reads
    #: Whether this module is genuinely computed from real per-point
    #: solver data in Real Physics mode today (see module docstring).
    real_in_real_physics: bool = False


COMPONENT_INFO: dict[str, ComponentInfo] = {
    "dynamic": ComponentInfo(
        key="dynamic",
        icon="🌀",
        label="Dynamic Complexity",
        description="Wind-driven complexity - real wind speed magnitude at this point.",
        formula="normalize_wind(wind_speed): clip to [0, 50] m/s, divide by 50",
        real_inputs=("wind_speed",),
        real_in_real_physics=True,
    ),
    "thermodynamic": ComponentInfo(
        key="thermodynamic",
        icon="🌡️",
        label="Thermodynamic Complexity",
        description="Real temperature + specific humidity blend.",
        formula=(
            "0.5 * normalize_temperature(T) + 0.5 * normalize_humidity(q); "
            "T: -30..50 °C -> (T+30)/80. q: 0..0.03 kg/kg -> q/0.03"
        ),
        real_inputs=("temperature", "specific_humidity"),
        real_in_real_physics=True,
    ),
    "convective": ComponentInfo(
        key="convective",
        icon="⛈️",
        label="Convective Complexity",
        description="Real CAPE/CIN-driven atmospheric instability.",
        formula=(
            "0.7 * normalize_cape(CAPE) + 0.3 * normalize_cin(CIN); "
            "CAPE: 0..5000 J/kg -> /5000. CIN: abs(), 0..500 J/kg -> /500"
        ),
        real_inputs=("cape", "cin"),
        real_in_real_physics=False,
    ),
    "microphysical": ComponentInfo(
        key="microphysical",
        icon="❄️",
        label="Microphysical Complexity",
        description="Real precipitation rate.",
        formula="normalize_precipitation(precip): clip to [0, 50] mm/h, divide by 50",
        real_inputs=("precipitation",),
        real_in_real_physics=False,
    ),
    "topographic": ComponentInfo(
        key="topographic",
        icon="⛰️",
        label="Topographic Complexity",
        description="Real terrain elevation underneath this point.",
        formula="normalize_topographic(altitude): clip to [0, 3000] m, divide by 3000",
        real_inputs=("altitude",),
        real_in_real_physics=False,
    ),
    "temporal": ComponentInfo(
        key="temporal",
        icon="🕐",
        label="Temporal Complexity",
        description="Real rate of change of the situation over time.",
        formula="normalize_temporal(temporal_change): clip to [0, 20], divide by 20",
        real_inputs=("temporal_change",),
        real_in_real_physics=False,
    ),
    "confidence": ComponentInfo(
        key="confidence",
        icon="❓",
        label="Uncertainty",
        description="Inverted forecast confidence - lower confidence means higher complexity.",
        formula="1 - normalize_confidence(confidence): clip to [0, 100]%, divide by 100",
        real_inputs=("confidence",),
        real_in_real_physics=False,
    ),
}


class AWCIComponentDetailDialog(QDialog):
    """Real per-module detail dialog - see module docstring for where
    every number/formula shown here comes from."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet(dashboard_stylesheet())
        self.resize(440, 320)

        outer = QVBoxLayout(self)
        self.header_label = QLabel("")
        self.header_label.setStyleSheet(label_style("text_primary", "lg", "bold"))
        outer.addWidget(self.header_label)

        self.description_label = QLabel("")
        self.description_label.setStyleSheet(label_style("text_secondary", "sm"))
        self.description_label.setWordWrap(True)
        outer.addWidget(self.description_label)

        self.score_label = QLabel("")
        self.score_label.setStyleSheet(label_style("text_primary", "md", "bold"))
        outer.addWidget(self.score_label)

        self.badge_label = QLabel("")
        self.badge_label.setWordWrap(True)
        outer.addWidget(self.badge_label)

        self.inputs_header = QLabel("Real inputs")
        self.inputs_header.setStyleSheet(label_style("text_secondary", "sm", "bold"))
        outer.addWidget(self.inputs_header)
        self.inputs_label = QLabel("")
        self.inputs_label.setStyleSheet(f"font-family: monospace; color: {TOKENS.text_primary}; font-size: 10px;")
        self.inputs_label.setWordWrap(True)
        outer.addWidget(self.inputs_label)

        self.formula_header = QLabel("Real formula")
        self.formula_header.setStyleSheet(label_style("text_secondary", "sm", "bold"))
        outer.addWidget(self.formula_header)
        self.formula_label = QLabel("")
        self.formula_label.setStyleSheet(f"font-family: monospace; color: {TOKENS.text_primary}; font-size: 10px;")
        self.formula_label.setWordWrap(True)
        outer.addWidget(self.formula_label)

        outer.addStretch()

    def show_component(self, key: str, score: float, raw_data: dict[str, Any] | None, mode: Mode) -> None:
        """(Re)populate every field for real module `key` and show the dialog."""
        info = COMPONENT_INFO[key]
        self.setWindowTitle(f"AWCI – {info.label}")
        self.header_label.setText(f"{info.icon}  {info.label}")
        self.description_label.setText(info.description)
        self.score_label.setText(f"Current score: {score:.1f} / 100")

        is_real = True if mode == "demo" else info.real_in_real_physics
        if is_real:
            self.badge_label.setText(f"✅ REAL - genuinely computed ({'demo synthetic pattern' if mode == 'demo' else 'Real Physics solver'})")
            self.badge_label.setStyleSheet(f"color: {TOKENS.success}; font-size: 10px; font-weight: bold;")
        else:
            self.badge_label.setText(
                "⚠ DEFAULT - not computed in Real Physics mode today "
                "(acf.awci.vertical_field.compute_real_complexity_volume() does not supply this input yet)"
            )
            self.badge_label.setStyleSheet(f"color: {TOKENS.warning}; font-size: 10px; font-weight: bold;")

        input_lines = []
        for field_name in info.real_inputs:
            if raw_data is not None and field_name in raw_data:
                input_lines.append(f"{field_name} = {raw_data[field_name]:.4g}")
            else:
                input_lines.append(f"{field_name} = (not supplied - AWCICalculator's own default applies)")
        self.inputs_label.setText("\n".join(input_lines))
        self.formula_label.setText(info.formula)

        self.show()
        self.raise_()
        self.activateWindow()
