"""
AWCI Dashboard
==============

Complete AWCI dashboard with gauge, decomposition, profile, timeline.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt

from typing import Optional, Dict, Any

from .awci_gauge import AWCIGauge
from .awci_decomposition import AWCIDecomposition


class AWCIDashboard(QWidget):
    """Complete AWCI Dashboard."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.gauge = AWCIGauge()
        self.decomposition = AWCIDecomposition()

        self._build_ui()
        self._apply_theme()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Header
        header = QLabel("AWCI – AVIATION WEATHER COMPLEXITY INDEX")
        header.setStyleSheet("color: #e0e0e0; font-size: 14px; font-weight: bold;")
        layout.addWidget(header)

        subheader = QLabel("Concept Output – Research Prototype")
        subheader.setStyleSheet("color: #8080a0; font-size: 11px;")
        layout.addWidget(subheader)

        # Top row: Gauge + Decomposition
        top_row = QHBoxLayout()
        top_row.addWidget(self.gauge)
        top_row.addWidget(self.decomposition)
        layout.addLayout(top_row)

        # Bottom: Info
        info = QLabel("SYNTHETIC VIEW • One map to understand the complexity")
        info.setStyleSheet("color: #606080; font-size: 10px; padding: 5px; border-top: 1px solid #2a2a4a;")
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)

        self.setLayout(layout)

    def _apply_theme(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a2e;
                color: #e0e0e0;
                font-family: 'Segoe UI', 'Ubuntu', sans-serif;
            }
            QFrame {
                background-color: #16213e;
                border: 1px solid #2a2a4a;
                border-radius: 8px;
            }
        """)

    def update_with_awci_result(self, result: Dict[str, Any]):
        """Update dashboard with AWCI result."""
        self.gauge.set_score(result.get('awci', 0))
        self.decomposition.set_decomposition(result.get('decomposition', {}))

    def set_data(self, awci_result: Dict[str, Any]):
        self.update_with_awci_result(awci_result)
