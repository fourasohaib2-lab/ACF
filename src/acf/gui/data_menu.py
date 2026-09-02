"""
ACF Data Menu

Gestion des opérations scientifiques sur les datasets.

NOTE (found, NOT changed — RÈGLE D'OR / single source of truth): never
constructed anywhere (confirmed by grep across src/). This class is
genuinely correct and functional (real Open/Info/Refresh/Close Dataset
handlers), but it is a near-duplicate of the Data menu
acf.gui.menu.MenuManager already builds (this session's earlier finding,
now wired into ClassicDashboardWindow) - same actions, same
window.data.open()/close()/current_dataset dependency, just calling
window.refresh_explorer() directly instead of going through
window.dashboard.get_panel("explorer"). Constructing both on the same
window would add a second, redundant "Data" menu to the menu bar. Not
deleted per project convention - flagged as the superseded one.
"""

from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QFileDialog,
    QMessageBox,
)


class DataMenuManager:
    """
    Menu Data ACF.
    """

    def __init__(self, window):

        self.window = window

        self.create()

    ##################################################

    def create(self):

        menu_bar = self.window.menuBar()

        data_menu = menu_bar.addMenu("Data")

        open_action = QAction("Open Dataset...", self.window)

        info_action = QAction("Dataset Information", self.window)

        catalog_action = QAction("Dataset Catalog", self.window)

        refresh_action = QAction("Refresh Explorer", self.window)

        close_action = QAction("Close Dataset", self.window)

        open_action.triggered.connect(self.open_dataset)

        info_action.triggered.connect(self.dataset_information)

        refresh_action.triggered.connect(self.window.refresh_explorer)

        close_action.triggered.connect(self.close_dataset)

        data_menu.addAction(open_action)

        data_menu.addAction(info_action)

        data_menu.addSeparator()

        data_menu.addAction(catalog_action)

        data_menu.addSeparator()

        data_menu.addAction(refresh_action)

        data_menu.addAction(close_action)

    ##################################################

    def open_dataset(self):

        filename, _ = QFileDialog.getOpenFileName(
            self.window,
            "Open Meteorological Dataset",
            "",
            """
            Scientific Data
            (*.grib *.grb *.grib2 *.nc *.nc4)
            """,
        )

        if not filename:
            return

        try:
            dataset = self.window.data.open(filename)

            self.window.statusBar().showMessage(f"Dataset loaded : {dataset.name}")

            self.window.refresh_explorer()

        except Exception as error:
            QMessageBox.critical(self.window, "Dataset Error", str(error))

    ##################################################

    def dataset_information(self):

        dataset = self.window.data.current_dataset

        if dataset is None:
            QMessageBox.warning(self.window, "Dataset", "No dataset loaded.")

            return

        QMessageBox.information(self.window, "Dataset Information", str(dataset.summary()))

    ##################################################

    def close_dataset(self):

        self.window.data.close()

        self.window.refresh_explorer()

        self.window.statusBar().showMessage("Dataset closed")
