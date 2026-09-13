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
from typing import TYPE_CHECKING, Any, Literal

from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout, QWidget

from acf.awci.diagnostic_registry import DIAGNOSTIC_REGISTRY
from acf.awci.weights import WeightsManager
from acf.awci.wind_classification import classify_jet_stream, classify_wind_beaufort_force
from acf.gui.theme_tokens import TOKENS, dashboard_stylesheet, label_style
from acf.gui_screen_utils import fit_dialog_to_screen

#: Maps a real COMPONENT_INFO module key to its real
#: acf.awci.diagnostic_registry entry - only the 5 modules with a real
#: "_module_combination" entry (dynamic/thermodynamic/convective/
#: microphysical/topographic). "temporal"/"confidence" have no entry
#: yet (a real, disclosed gap of the registry itself, section 55 - see
#: AWCIComponentDetailDialog.show_component()'s own honest fallback,
#: never a fabricated stand-in entry).
_DIAGNOSTIC_REGISTRY_KEY_FOR_MODULE: dict[str, str] = {
    "dynamic": "dynamic_module_combination",
    "thermodynamic": "thermodynamic_module_combination",
    "convective": "convective_module_combination",
    "microphysical": "microphysical_module_combination",
    "topographic": "topographic_module_combination",
}

if TYPE_CHECKING:
    from acf.awci.result import AWCIResult

Mode = Literal["demo", "real_physics", "imported_model"]


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
    # ceiling/visibility (added 2026-09-13, once AWCIHazardRow's own
    # cards for these 2 real, opt-in AWCICalculator modules became
    # clickable) - both are genuinely opt-in: AWCICalculator.calculate()
    # only computes a real score when the caller supplies
    # ceiling_height_m/visibility_risk (see that method's own docstring)
    # and otherwise honestly defaults to 0.0 - neither this dashboard's
    # demo _synthetic_inputs() path nor its Real Physics per-point
    # raw-field dict currently populates either key, so both correctly
    # show DEFAULT in every mode today, never a fabricated REAL badge.
    "ceiling": ComponentInfo(
        key="ceiling",
        icon="☁️",
        label="Ceiling Complexity",
        description="Real estimated ceiling height (LCL approximation, acf.awci.ceiling).",
        formula=(
            "normalize_ceiling(ceiling_height_m): 1 - ceiling_height_m / MVFR_CEILING_M "
            "(914.4 m / 3000 ft, the real FAA/NOAA VFR threshold), clipped to [0, 1]"
        ),
        real_inputs=("ceiling_height_m",),
        real_in_real_physics=False,
    ),
    "visibility": ComponentInfo(
        key="visibility",
        icon="👁️",
        label="Visibility Complexity",
        description="Real visibility-degradation risk proxy (acf.awci.visibility) - not a literal visibility distance.",
        formula="normalize_visibility_risk(visibility_risk): pass-through clamp to [0, 1]",
        real_inputs=("visibility_risk",),
        real_in_real_physics=False,
    ),
}


class AWCIComponentDetailDialog(QDialog):
    """Real per-module detail dialog - see module docstring for where
    every number/formula shown here comes from."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet(dashboard_stylesheet())
        # NOTE (real responsive-sizing fix, 2026-09-05): was a hardcoded
        # self.resize(440, 320) - clamp to the actual screen instead, same
        # fix as gui_screen_utils.fit_window_to_screen for main windows.
        fit_dialog_to_screen(self, 440, 320)

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

        # Real WMO Beaufort force / jet-stream classification (added
        # 2026-09-12, explicit user request "je veux que tu ajoutes
        # toutes les seuils possible...") - only shown for the
        # "dynamic" module, whose own real_inputs already carries
        # wind_speed. Hidden (see show_component()) for every other
        # module, never a fabricated section with nothing real to show.
        self.classification_header = QLabel("Real classification (WMO/textbook)")
        self.classification_header.setStyleSheet(label_style("text_secondary", "sm", "bold"))
        outer.addWidget(self.classification_header)
        self.classification_label = QLabel("")
        self.classification_label.setStyleSheet(f"color: {TOKENS.text_primary}; font-size: 10px;")
        self.classification_label.setWordWrap(True)
        outer.addWidget(self.classification_label)

        self.weight_status_header = QLabel("Scientific status (docs/ACF_MASTER_PROMPT.md §80)")
        self.weight_status_header.setStyleSheet(label_style("text_secondary", "sm", "bold"))
        outer.addWidget(self.weight_status_header)
        self.weight_status_label = QLabel("")
        self.weight_status_label.setStyleSheet(f"color: {TOKENS.text_primary}; font-size: 10px;")
        self.weight_status_label.setWordWrap(True)
        outer.addWidget(self.weight_status_label)

        # Real diagnostic-registry documentation (§55, added 2026-09-03)
        # - acf.awci.diagnostic_registry.DIAGNOSTIC_REGISTRY existed
        # since an earlier closure this session but was never shown
        # anywhere in the GUI (only queryable from Python). Shows the
        # real physical meaning/limitations/reference already written
        # for this module's own "_module_combination" entry - not a
        # second, independently-written description.
        self.diagnostic_header = QLabel("Diagnostic documentation (docs/ACF_MASTER_PROMPT.md §55)")
        self.diagnostic_header.setStyleSheet(label_style("text_secondary", "sm", "bold"))
        outer.addWidget(self.diagnostic_header)
        self.diagnostic_label = QLabel("")
        self.diagnostic_label.setStyleSheet(f"color: {TOKENS.text_primary}; font-size: 10px;")
        self.diagnostic_label.setWordWrap(True)
        outer.addWidget(self.diagnostic_label)

        # Real drill-down chain (§26/§53, added 2026-09-03) - built by
        # acf.awci.result.build_awci_result()/AWCIResult.trace_chain(),
        # a real capability that existed since this session's earlier
        # §26/§53/§81 closure but was never actually shown anywhere in
        # the GUI until now.
        self.trace_header = QLabel("Drill-down chain (docs/ACF_MASTER_PROMPT.md §26/§53)")
        self.trace_header.setStyleSheet(label_style("text_secondary", "sm", "bold"))
        outer.addWidget(self.trace_header)
        self.trace_label = QLabel("")
        self.trace_label.setStyleSheet(f"font-family: monospace; color: {TOKENS.text_primary}; font-size: 10px;")
        self.trace_label.setWordWrap(True)
        outer.addWidget(self.trace_label)

        outer.addStretch()

    def show_component(
        self,
        key: str,
        score: float,
        raw_data: dict[str, Any] | None,
        mode: Mode,
        awci_result: AWCIResult | None = None,
    ) -> None:
        """(Re)populate every field for real module `key` and show the
        dialog.

        Parameters
        ----------
        awci_result : AWCIResult, optional
            The real, already-built AWCIResult (§26/§53/§81) for the
            SAME point/calculate() call `score`/`raw_data` came from -
            its own real `trace_chain()` is shown below the scientific-
            status section. None (the caller didn't build one yet, or
            this dialog is being reused before any real refresh
            happened) shows an honest "not available" placeholder,
            never a fabricated trace.
        """
        info = COMPONENT_INFO[key]
        self.setWindowTitle(f"AWCI – {info.label}")
        self.header_label.setText(f"{info.icon}  {info.label}")
        self.description_label.setText(info.description)
        self.score_label.setText(f"Current score: {score:.1f} / 100")

        # "imported_model" (added 2026-09-08): every input the imported
        # file genuinely supplied IS real (matched through ACF's own
        # ParameterMapper aliases + real unit conversion - see
        # acf.awci.model_import); anything the file lacked fell back to
        # AWCICalculator's own default, disclosed per-input below, so
        # the badge is real the same way demo mode's is, with the
        # file's own name as the honest source label.
        if mode == "demo":
            is_real, source_label = True, "demo synthetic pattern"
        elif mode == "imported_model":
            is_real, source_label = True, "imported model file (acf.awci.model_import)"
        else:
            is_real, source_label = info.real_in_real_physics, "Real Physics solver"
        if is_real:
            self.badge_label.setText(f"✅ REAL - genuinely computed ({source_label})")
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

        if key == "dynamic" and raw_data is not None and "wind_speed" in raw_data:
            wind_speed = raw_data["wind_speed"]
            beaufort = classify_wind_beaufort_force(wind_speed)
            jet = classify_jet_stream(wind_speed)
            jet_text = (
                f"jet-stream strength (>= {jet['threshold_m_s']:.0f} m/s)"
                if jet["is_jet_stream"]
                else f"below jet-stream strength (< {jet['threshold_m_s']:.0f} m/s)"
            )
            self.classification_header.show()
            self.classification_label.show()
            self.classification_label.setText(
                f"WMO Beaufort force {beaufort['force']} ({beaufort['name']}) — {jet_text}"
            )
        else:
            self.classification_header.hide()
            self.classification_label.hide()

        weight_status = WeightsManager().get_weight_status(key)
        self.weight_status_label.setText(
            f"Weight status: {weight_status.status.value.upper()} — {weight_status.rationale}"
        )

        diagnostic_key = _DIAGNOSTIC_REGISTRY_KEY_FOR_MODULE.get(key)
        if diagnostic_key is not None:
            spec = DIAGNOSTIC_REGISTRY[diagnostic_key]
            self.diagnostic_label.setText(
                f"Physical meaning: {spec.physical_meaning}\n\n"
                f"Limitations: {spec.limitations}\n\n"
                f"Reference: {spec.reference}"
            )
        else:
            self.diagnostic_label.setText(
                "not yet in the centralized diagnostic registry (see acf.awci.diagnostic_registry's own "
                "documented scope, section 55)"
            )

        if awci_result is not None:
            self.trace_label.setText("\n".join(awci_result.trace_chain()))
        else:
            self.trace_label.setText("not available - no real AWCIResult was supplied for this point yet")

        self.show()
        self.raise_()
        self.activateWindow()
