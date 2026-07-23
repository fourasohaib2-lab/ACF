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

from acf.data.manager import DataManager



class MenuManager:
    """
    Gestionnaire des menus ACF.
    """


    def __init__(self, window):

        self.window = window

        self.recent_menu = None

        # Scientific Data Engine
        self.data_manager = DataManager()

        self.create()



    ##################################################
    # CREATE MENUS
    ##################################################

    def create(self):

        menu_bar = self.window.menuBar()


        ############################
        # FILE
        ############################

        file_menu = menu_bar.addMenu(
            "File"
        )


        ############################
        # OTHER MENUS
        ############################

        menu_bar.addMenu("Edit")
        menu_bar.addMenu("View")

        data_menu = menu_bar.addMenu(
            "Data"
        )

        menu_bar.addMenu("Tools")
        menu_bar.addMenu("Plugins")
        menu_bar.addMenu("Help")



        ############################
        # FILE ACTIONS
        ############################

        new_action = QAction(
            "New Project...",
            self.window
        )


        open_action = QAction(
            "Open Project...",
            self.window
        )


        save_action = QAction(
            "Save Project",
            self.window
        )


        close_action = QAction(
            "Close Project",
            self.window
        )


        properties_action = QAction(
            "Project Properties",
            self.window
        )


        exit_action = QAction(
            "Exit",
            self.window
        )



        self.recent_menu = file_menu.addMenu(
            "Recent Projects"
        )



        new_action.triggered.connect(
            self.new_project
        )


        open_action.triggered.connect(
            self.open_project
        )


        save_action.triggered.connect(
            self.save_project
        )


        close_action.triggered.connect(
            self.close_project
        )


        properties_action.triggered.connect(
            self.show_project_properties
        )


        exit_action.triggered.connect(
            self.window.close
        )



        file_menu.addAction(
            new_action
        )


        file_menu.addAction(
            open_action
        )


        file_menu.addSeparator()


        file_menu.addMenu(
            self.recent_menu
        )


        file_menu.addSeparator()


        file_menu.addAction(
            properties_action
        )


        file_menu.addAction(
            save_action
        )


        file_menu.addAction(
            close_action
        )


        file_menu.addSeparator()


        file_menu.addAction(
            exit_action
        )



        ############################
        # DATA ACTIONS
        ############################


        open_dataset_action = QAction(
            "Open Dataset...",
            self.window
        )


        dataset_info_action = QAction(
            "Dataset Information",
            self.window
        )


        validate_dataset_action = QAction(
            "Validate Dataset",
            self.window
        )



        open_dataset_action.triggered.connect(
            self.open_dataset
        )


        dataset_info_action.triggered.connect(
            self.dataset_information
        )


        validate_dataset_action.triggered.connect(
            self.validate_dataset
        )



        data_menu.addAction(
            open_dataset_action
        )


        data_menu.addSeparator()


        data_menu.addAction(
            dataset_info_action
        )


        data_menu.addAction(
            validate_dataset_action
        )



        self.update_recent_projects()



    ##################################################
    # RECENT PROJECTS
    ##################################################

    def update_recent_projects(self):

        self.recent_menu.clear()


        projects = (
            self.window.workspace
            .recent_projects()
        )


        if not projects:

            action = QAction(
                "No recent projects",
                self.window
            )

            action.setEnabled(False)

            self.recent_menu.addAction(
                action
            )

            return



        for project_file in projects:

            path = Path(
                project_file
            )


            action = QAction(
                path.parent.name,
                self.window
            )


            action.triggered.connect(
                lambda checked=False,
                file=project_file:
                self.open_recent_project(file)
            )


            self.recent_menu.addAction(
                action
            )



    def open_recent_project(self, filename):

        project = (
            self.window.workspace
            .open_project(filename)
        )

        self.load_project_to_interface(
            project
        )

        self.update_recent_projects()



    ##################################################
    # PROJECT MANAGEMENT
    ##################################################

    def new_project(self):

        dialog = NewProjectDialog(
            self.window
        )


        if dialog.exec():

            data = dialog.project_data()


            project = (
                self.window.workspace
                .create_project(
                    name=data["name"],
                    directory=data["directory"],
                    author=data["author"],
                    description=data["description"],
                )
            )


            self.load_project_to_interface(
                project
            )


            self.update_recent_projects()



    def open_project(self):

        filename, _ = QFileDialog.getOpenFileName(
            self.window,
            "Open ACF Project",
            "",
            "ACF Project (*.acf)"
        )


        if not filename:

            return


        try:

            project = (
                self.window.workspace
                .open_project(filename)
            )


            self.load_project_to_interface(
                project
            )


            self.update_recent_projects()


        except Exception as error:

            QMessageBox.critical(
                self.window,
                "Open Error",
                str(error)
            )



    def save_project(self):

        try:

            self.window.workspace.save_project()


            self.window.statusBar().showMessage(
                "Project saved"
            )


        except Exception as error:

            QMessageBox.warning(
                self.window,
                "Save Error",
                str(error)
            )



    def close_project(self):

        self.window.workspace.close_project()


        self.window.dashboard.clear_project()


        self.window.setWindowTitle(
            "Atmospheric Complexity Framework"
        )


        self.window.statusBar().showMessage(
            "No project opened."
        )



    def show_project_properties(self):

        project = (
            self.window.workspace.project()
        )


        if project is None:

            QMessageBox.warning(
                self.window,
                "Project Properties",
                "No project opened."
            )

            return



        dialog = ProjectPropertiesDialog(
            project,
            self.window
        )


        if dialog.exec():

            dialog.update_project()

            self.window.workspace.save_project()



    def load_project_to_interface(self, project):

        explorer = (
            self.window.dashboard
            .get_panel("explorer")
        )


        if explorer:

            explorer.load_project(
                project
            )



        self.window.setWindowTitle(
            "Atmospheric Complexity Framework - "
            + project.name
        )



    ##################################################
    # DATA MANAGEMENT
    ##################################################

    def open_dataset(self):

        filename, _ = QFileDialog.getOpenFileName(
            self.window,
            "Open Meteorological Dataset",
            "",
            "Scientific Files (*.nc *.nc4 *.grib *.grib2 *.grb)"
        )


        if not filename:

            return


        try:

            dataset = (
                self.data_manager
                .open(filename)
            )


            self.data_manager.current_dataset = dataset


            self.window.statusBar().showMessage(
                "Dataset loaded"
            )


        except Exception as error:


            QMessageBox.critical(
                self.window,
                "Dataset Error",
                str(error)
            )



    def dataset_information(self):

        dataset = (
            self.data_manager.current_dataset
        )


        if dataset is None:

            QMessageBox.information(
                self.window,
                "Dataset",
                "No dataset loaded."
            )

            return


        QMessageBox.information(
            self.window,
            "Dataset Information",
            str(dataset.summary())
        )



    def validate_dataset(self):

        dataset = (
            self.data_manager.current_dataset
        )


        if dataset is None:

            QMessageBox.warning(
                self.window,
                "Validation",
                "No dataset loaded."
            )

            return



        result = dataset.validate()


        QMessageBox.information(
            self.window,
            "Validation Result",
            str(result)
        )
