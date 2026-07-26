#!/usr/bin/env python3
"""Test AWCI Dashboard."""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout

from acf.gui.dashboard.awci_dashboard import AWCIDashboard


def create_test_data():
    return {
        'awci': 62.5,
        'decomposition': {
            'dynamic': 40.0,
            'thermodynamic': 30.0,
            'convective': 20.0,
            'microphysical': 10.0,
            'topographic': 8.0,
            'temporal': 7.0,
            'confidence': 5.0,
        }
    }


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AWCI Dashboard")
        self.setGeometry(100, 100, 700, 500)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        central.setLayout(layout)

        self.dashboard = AWCIDashboard()
        layout.addWidget(self.dashboard)

        data = create_test_data()
        self.dashboard.update_with_awci_result(data)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
