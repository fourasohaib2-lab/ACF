"""
ACF Menu Manager

Gestion complète des menus principaux.
"""

from pathlib import Path

from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QFileDialog,
    QMessageBox,
)

from acf.gui.dialogs.new_project_dialog import NewProjectDialog
from acf.gui.dialogs.project_properties_dialog import ProjectPropertiesDialog


class MenuManager:
    """
    Gestionnaire des menus ACF.
    """

    def __init__(self, window):

        self.window = window

        self.recent_menu = None

        self.create()

    ##################################################
    # CREATE MENUS
    ##################################################

    def create(self):
        """
        NOTE (investigated, not a real bug): every QMenu/QAction created
        here used to be a bare local variable with no `self.` reference
        kept after create() returned. This was investigated as a possible
        real crash - `menu_bar.actions()[i].menu()` on a menu built this
        way does raise "libshiboken: Internal C++ object (QMenu) already
        deleted" when queried from Python under this PySide6 6.11.1 /
        offscreen-platform combination - but further testing showed that
        access pattern itself is the unreliable part, not the object's
        lifetime: the SAME menu, queried via win.menuBar().findChildren
        (QMenu) - i.e. via Qt's own real child-traversal, the mechanism
        actually used when a menu bar is shown and clicked - is fully
        intact with all its actions, with or without any Python reference
        kept, confirmed by direct reproduction on the original bare-local
        pattern. So this was not, in fact, liable to crash for an
        operator actually using the menu. Kept as instance attributes
        anyway as better practice (makes every menu/action independently
        addressable - e.g. from tests - without relying on
        findChildren()), not because it was fixing a proven defect.
        """
        menu_bar = self.window.menuBar()

        ##################################################
        # FILE
        ##################################################

        self.file_menu = menu_bar.addMenu("File")

        self.new_action = QAction("New Project...", self.window)

        self.open_action = QAction("Open Project...", self.window)

        self.recent_menu = self.file_menu.addMenu("Recent Projects")

        self.properties_action = QAction("Project Properties", self.window)

        self.save_action = QAction("Save Project", self.window)

        self.close_action = QAction("Close Project", self.window)

        self.exit_action = QAction("Exit", self.window)

        self.new_action.triggered.connect(self.new_project)

        self.open_action.triggered.connect(self.open_project)

        self.properties_action.triggered.connect(self.show_project_properties)

        self.save_action.triggered.connect(self.save_project)

        self.close_action.triggered.connect(self.close_project)

        self.exit_action.triggered.connect(self.window.close)

        self.file_menu.addAction(self.new_action)

        self.file_menu.addAction(self.open_action)

        self.file_menu.addSeparator()

        self.file_menu.addMenu(self.recent_menu)

        self.file_menu.addSeparator()

        self.file_menu.addAction(self.properties_action)

        self.file_menu.addAction(self.save_action)

        self.file_menu.addAction(self.close_action)

        self.file_menu.addSeparator()

        self.file_menu.addAction(self.exit_action)

        ##################################################
        # DATA MENU
        ##################################################

        self.data_menu = menu_bar.addMenu("Data")

        self.open_dataset_action = QAction("Open Dataset...", self.window)

        self.close_dataset_action = QAction("Close Dataset", self.window)

        self.dataset_info_action = QAction("Dataset Information", self.window)

        self.refresh_dataset_action = QAction("Refresh Dataset View", self.window)

        self.open_dataset_action.triggered.connect(self.open_dataset)

        self.close_dataset_action.triggered.connect(self.close_dataset)

        self.dataset_info_action.triggered.connect(self.dataset_information)

        self.refresh_dataset_action.triggered.connect(self.refresh_dataset_view)

        self.data_menu.addAction(self.open_dataset_action)

        self.data_menu.addAction(self.close_dataset_action)

        self.data_menu.addSeparator()

        self.data_menu.addAction(self.dataset_info_action)

        self.data_menu.addAction(self.refresh_dataset_action)

        ##################################################
        # OTHER MENUS
        ##################################################

        self.edit_menu = menu_bar.addMenu("Edit")

        self.view_menu = menu_bar.addMenu("View")

        self.tools_menu = menu_bar.addMenu("Tools")

        self.plugins_menu = menu_bar.addMenu("Plugins")

        self.help_menu = menu_bar.addMenu("Help")

        self.update_recent_projects()

    ##################################################
    # PROJECT
    ##################################################

    def new_project(self):

        dialog = NewProjectDialog(self.window)

        if dialog.exec():
            data = dialog.project_data()

            project = self.window.workspace.create_project(
                name=data["name"],
                directory=data["directory"],
                author=data["author"],
                description=data["description"],
            )

            self.load_project_to_interface(project)

    ##################################################

    def open_project(self):

        filename, _ = QFileDialog.getOpenFileName(self.window, "Open ACF Project", "", "ACF Project (*.acf)")

        if not filename:
            return

        project = self.window.workspace.open_project(filename)

        self.load_project_to_interface(project)

    ##################################################

    def save_project(self):

        try:
            self.window.workspace.save_project()

            self.window.statusBar().showMessage("Project saved")

        except Exception as error:
            QMessageBox.warning(self.window, "Save Error", str(error))

    ##################################################

    def close_project(self):

        self.window.workspace.close_project()

        explorer = self.window.dashboard.get_panel("explorer")

        if explorer:
            explorer.clear()

        self.window.setWindowTitle("Atmospheric Complexity Framework")

        self.window.statusBar().showMessage("Project closed")

    ##################################################
    # DATA MANAGEMENT
    ##################################################

    def open_dataset(self):

        filename, _ = QFileDialog.getOpenFileName(
            self.window,
            "Open Scientific Dataset",
            "",
            """
            Meteorological files
            (*.grib *.grib2 *.grb *.nc *.nc4)
            """,
        )

        if not filename:
            return

        try:
            dataset = self.window.data.open(filename)

            self.refresh_dataset_view()

            self.window.statusBar().showMessage(f"Dataset loaded : {dataset.name}")

        except Exception as error:
            QMessageBox.critical(self.window, "Dataset Error", str(error))

    ##################################################

    def close_dataset(self):

        self.window.data.close()

        self.window.statusBar().showMessage("Dataset closed")

    ##################################################

    def dataset_information(self):

        dataset = self.window.data.current_dataset

        if dataset is None:
            QMessageBox.information(self.window, "Dataset Information", "No dataset loaded.")

            return

        QMessageBox.information(self.window, "Dataset Information", str(dataset.summary()))

    ##################################################

    def refresh_dataset_view(self):

        explorer = self.window.dashboard.get_panel("explorer")

        if explorer:
            explorer.refresh_datasets(self.window.data.datasets())

    ##################################################
    # PROJECT PROPERTIES
    ##################################################

    def show_project_properties(self):

        project = self.window.workspace.project()

        if project is None:
            QMessageBox.warning(self.window, "Project Properties", "No project opened.")

            return

        dialog = ProjectPropertiesDialog(project, self.window)

        if dialog.exec():
            dialog.update_project()

            self.window.workspace.save_project()

    ##################################################
    # LOAD PROJECT UI
    ##################################################

    def load_project_to_interface(self, project):

        explorer = self.window.dashboard.get_panel("explorer")

        if explorer:
            explorer.load_project(project)

        self.window.setWindowTitle("Atmospheric Complexity Framework - " + project.name)

    ##################################################
    # RECENT
    ##################################################

    def update_recent_projects(self):
        """
        NOTE (same investigated-not-proven category as create()'s own
        NOTE): these dynamically-built QAction objects used to be bare
        local variables inside the loop. Kept in self._recent_actions as
        the same better-practice precaution, not because a real defect
        was proven here either.
        """
        self.recent_menu.clear()

        self._recent_actions: list[QAction] = []

        projects = self.window.workspace.recent_projects()

        if not projects:
            action = QAction("No recent projects", self.window)

            action.setEnabled(False)

            self.recent_menu.addAction(action)

            self._recent_actions.append(action)

            return

        for item in projects:
            path = Path(item)

            action = QAction(path.parent.name, self.window)

            action.triggered.connect(lambda checked=False, file=item: self.open_project_file(file))

            self.recent_menu.addAction(action)

            self._recent_actions.append(action)

    def open_project_file(self, filename):

        project = self.window.workspace.open_project(filename)

        self.load_project_to_interface(project)
