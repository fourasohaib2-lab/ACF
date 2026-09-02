"""
Atmospheric Complexity Framework (ACF)

DASHBOARD - Map Panel

Purpose:
--------
Provides Map Panel functionality for the ACF framework.

Responsibilities:
-----------------
• Manage map panel logic and state representations.
• Integrate with the dashboard subsystem of the ACF scientific engine.

Major Components:
-----------------
• MapPanel

Dependencies:
-------------
• Python Standard Library and NumPy/Scientific Python Stack.
• Internal acf.dashboard module infrastructure.

Scientific Context:
-------------------
Provides foundational capabilities for numerical weather prediction, atmospheric data processing,
physical modeling, and spatial-temporal analysis within the Atmospheric Complexity Framework.

NOTE (found, NOT changed — RÈGLE D'OR / single source of truth): never
constructed anywhere (confirmed by grep across src/) - unlike its
siblings in this same package (`ChartPanel`/`StatusPanel`/
`TimelinePanel`, each genuinely used elsewhere), nothing ever
instantiates this `MapPanel`. It is itself honest about being a
placeholder ("Interactive map will appear here" - no fabricated data),
and real map panels are covered elsewhere for real
(`acf.gui.dashboard.awci_map_panel.AWCIMapPanel`, genuinely used by
`AWCIDashboardWindow`). Not deleted per project convention. See
docs/architecture/duplicate_components.md for the broader pattern.
"""

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class MapPanel(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        title = QLabel("🌍 Main Map")
        title.setStyleSheet("font-size:18px;font-weight:bold;")

        placeholder = QLabel("Interactive map will appear here.")

        placeholder.setMinimumHeight(500)

        layout.addWidget(title)
        layout.addWidget(placeholder)
