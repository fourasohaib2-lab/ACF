"""
AWCI Summary Stats Bar
======================

Row of 5 stat boxes (Global Mean AWCI, Max AWCI, Area with AWCI>60,
Forecast Confidence, Model) matching the reference mockup's stats strip
under the global map. Every value is computed from the same real AWCI
grid the map panel draws (see awci_synthetic_field.py for what is and
is not synthetic).
"""

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget


class _StatBox(QFrame):
    def __init__(self, title: str) -> None:
        super().__init__()
        self.setStyleSheet("border: none;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(2)

        self.value_lbl = QLabel("—")
        self.value_lbl.setStyleSheet("color: #e0e0e0; font-size: 20px; font-weight: bold; border: none;")
        layout.addWidget(self.value_lbl)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: #8090a8; font-size: 9px; border: none;")
        layout.addWidget(title_lbl)

    def set_value(self, text: str, color: str = "#e0e0e0") -> None:
        self.value_lbl.setText(text)
        self.value_lbl.setStyleSheet(f"color: {color}; font-size: 20px; font-weight: bold; border: none;")


class AWCIStatsBar(QWidget):
    """Row of summary stat boxes below the global map."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet("background-color: #16213e; border: 1px solid #2a3a5a; border-radius: 6px;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)

        self.mean_box = _StatBox("GLOBAL MEAN AWCI")
        self.max_box = _StatBox("MAX AWCI")
        self.area_box = _StatBox("AREA WITH AWCI > 60")
        self.confidence_box = _StatBox("FORECAST CONFIDENCE")
        self.model_box = _StatBox("MODEL")

        for box in (self.mean_box, self.max_box, self.area_box, self.confidence_box, self.model_box):
            layout.addWidget(box)

        self.model_box.set_value("ACF Demo Grid")

    def update_data(self, flat_scores: list[float], confidence_pct: float = 75.0) -> None:
        if not flat_scores:
            return
        mean_v = sum(flat_scores) / len(flat_scores)
        max_v = max(flat_scores)
        area_pct = 100.0 * sum(1 for s in flat_scores if s > 60) / len(flat_scores)

        from acf.gui.dashboard.awci_colors import qcolor_for

        def hexcolor(v: float) -> str:
            c = qcolor_for(v)
            return f"#{c.red():02x}{c.green():02x}{c.blue():02x}"

        self.mean_box.set_value(f"{mean_v:.0f}", hexcolor(mean_v))
        self.max_box.set_value(f"{max_v:.0f}", hexcolor(max_v))
        self.area_box.set_value(f"{area_pct:.1f}%")
        self.confidence_box.set_value(f"{confidence_pct:.0f}%")
