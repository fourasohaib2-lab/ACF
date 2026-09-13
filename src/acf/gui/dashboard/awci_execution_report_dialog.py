"""
AWCI Execution Report Dialog
=============================

Real GUI surface for `acf.awci.execution_report.summarize_execution()`
(docs/ACF_MASTER_PROMPT.md §75 - "Le pipeline doit produire : logs,
metrics, warnings, errors, quality reports, runtime statistics.").
Explicit user request "je veux rendre tout les boutons de awci en
marche" led into this closure: the §75 report existed only as a real,
tested Python object with no GUI surface - this dialog is that surface,
reading the exact real `AWCIResult` the dashboard's own point-of-
interest pipeline already built (never a second/recomputed value).

Provenance / traceability section (added 2026-09-13, closing Master
Prompt V3 §25's "Where did this AWCI value come from?" - the user
must be able to answer model/cycle/forecast hour/grid/source/
processing version/timestamp): appends `AWCIResult.trace_chain()`'s own
real, ordered chain (Score -> Contributions -> Variables ->
Diagnostics -> données sources -> modèle -> échéance -> niveau
vertical, docs/ACF_MASTER_PROMPT.md §26/§53) below the §75 report -
the SAME real object `AWCIComponentDetailDialog`'s own trace_label
already renders, reused here rather than recomputed, so both dialogs
can never silently disagree about the same real result's provenance.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QDialog, QLabel, QScrollArea, QVBoxLayout, QWidget

from acf.awci.execution_report import summarize_execution
from acf.gui.theme_tokens import TOKENS, dashboard_stylesheet, label_style
from acf.gui_screen_utils import fit_dialog_to_screen

if TYPE_CHECKING:
    from acf.awci.result import AWCIResult

#: Real, disclosed color per Quality/AWCI-generated bucket - matches
#: this project's own established convention (awci_colors.risk_qcolor())
#: of a real, fixed color per real classification word, never guessed
#: per-call.
_QUALITY_COLOR = {
    "GOOD": TOKENS.text_primary,
    "DEGRADED": "#e3a544",
    "BAD": "#ff6b7f",
    "UNKNOWN": TOKENS.text_muted,
}


class AWCIExecutionReportDialog(QDialog):
    """Real §75 execution report viewer - one line per real field, no
    fabricated placeholder line."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("AWCI – Execution Report")
        # NOTE (real responsive-sizing fix, 2026-09-05): was a hardcoded
        # self.resize(420, 320) - clamp to the actual screen instead, same
        # fix as gui_screen_utils.fit_window_to_screen for main windows.
        # Widened/heightened 2026-09-13 once the real provenance section
        # (below) made the honest content genuinely longer than the
        # original §75-only report - still just a starting size, not a
        # hard cap (the scroll area below handles anything taller).
        fit_dialog_to_screen(self, 480, 440)
        self.setStyleSheet(dashboard_stylesheet())

        outer = QVBoxLayout(self)
        header = QLabel("📊 EXECUTION REPORT")
        header.setStyleSheet(label_style("text_primary", "lg", "bold"))
        outer.addWidget(header)

        subtitle = QLabel("Real per-execution report for the current point of interest (docs/ACF_MASTER_PROMPT.md §75).")
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet(label_style("text_secondary", "xs"))
        outer.addWidget(subtitle)

        # Real scroll area (added 2026-09-13, alongside the provenance
        # section below) - the combined §75 report + full trace_chain()
        # is genuinely taller than this dialog's own starting size on a
        # real point with several matched variables; scrolling beats
        # clipping or silently dropping real content.
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        rows_widget = QWidget()
        self.rows_container = QVBoxLayout(rows_widget)
        scroll.setWidget(rows_widget)
        outer.addWidget(scroll, stretch=1)
        self._row_labels: list[QLabel] = []

    def refresh(self, result: AWCIResult | None) -> None:
        """Rebuild every row from a real, freshly-supplied `AWCIResult`
        - never left showing a stale prior point's report. `result`
        being `None` (no real point-of-interest result computed yet)
        shows one honest placeholder line, not a fabricated report."""
        for label in self._row_labels:
            label.setParent(None)
        self._row_labels = []

        if result is None:
            label = QLabel("Not available yet - no real AWCI result computed for a point of interest.")
            label.setStyleSheet(label_style("text_muted", "sm"))
            self.rows_container.addWidget(label)
            self._row_labels.append(label)
            return

        report = summarize_execution(result)
        for line in report.render():
            label = QLabel(line)
            field_name = line.split(":")[0]
            color = TOKENS.text_primary
            if field_name == "Quality":
                color = _QUALITY_COLOR.get(report.quality, TOKENS.text_primary)
            elif field_name == "AWCI generated":
                color = TOKENS.text_primary if report.awci_generated else "#ff6b7f"
            label.setStyleSheet(f"color: {color}; font-size: 12px; font-family: monospace;")
            self.rows_container.addWidget(label)
            self._row_labels.append(label)

        # Provenance / traceability section - see module docstring.
        provenance_header = QLabel("📜 PROVENANCE / TRACEABILITY")
        provenance_header.setStyleSheet(label_style("text_primary", "md", "bold"))
        self.rows_container.addWidget(provenance_header)
        self._row_labels.append(provenance_header)
        for line in result.trace_chain():
            label = QLabel(line)
            label.setWordWrap(True)
            label.setStyleSheet(f"color: {TOKENS.text_secondary}; font-size: 11px; font-family: monospace;")
            self.rows_container.addWidget(label)
            self._row_labels.append(label)
