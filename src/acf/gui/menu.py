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

        menu_bar = self.window.menuBar()


        ##################################################
        # FILE
        ##################################################

        file_menu = menu_bar.addMenu(
            "File"
        )


        new_action = QAction(
            "New Project...",
            self.window
        )


        open_action = QAction(
            "Open Project...",
            self.window
        )


        self.recent_menu = file_menu.addMenu(
            "Recent Projects"
        )


        properties_action = QAction(
            "Project Properties",
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


        exit_action = QAction(
            "Exit",
            self.window
        )



        new_action.triggered.connect(
            self.new_project
        )

        open_action.triggered.connect(
            self.open_project
        )

        properties_action.triggered.connect(
            self.show_project_properties
        )

        save_action.triggered.connect(
            self.save_project
        )

        close_action.triggered.connect(
            self.close_project
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



        ##################################################
        # DATA MENU
        ##################################################

        data_menu = menu_bar.addMenu(
            "Data"
        )


        open_dataset_action = QAction(
            "Open Dataset...",
            self.window
        )


        close_dataset_action = QAction(
            "Close Dataset",
            self.window
        )


        dataset_info_action = QAction(
            "Dataset Information",
            self.window
        )


        refresh_dataset_action = QAction(
            "Refresh Dataset View",
            self.window
        )



        open_dataset_action.triggered.connect(
            self.open_dataset
        )


        close_dataset_action.triggered.connect(
            self.close_dataset
        )


        dataset_info_action.triggered.connect(
            self.dataset_information
        )


        refresh_dataset_action.triggered.connect(
            self.refresh_dataset_view
        )



        data_menu.addAction(
            open_dataset_action
        )

        data_menu.addAction(
            close_dataset_action
        )

        data_menu.addSeparator()

        data_menu.addAction(
            dataset_info_action
        )

        data_menu.addAction(
            refresh_dataset_action
        )



        ##################################################
        # OTHER MENUS
        ##################################################

        menu_bar.addMenu(
            "Edit"
        )

        menu_bar.addMenu(
            "View"
        )

        menu_bar.addMenu(
            "Tools"
        )

        menu_bar.addMenu(
            "Plugins"
        )

        menu_bar.addMenu(
            "Help"
        )



        self.update_recent_projects()



    ##################################################
    # PROJECT
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



    ##################################################


    def open_project(self):

        filename,_ = QFileDialog.getOpenFileName(
            self.window,
            "Open ACF Project",
            "",
            "ACF Project (*.acf)"
        )


        if not filename:

            return


        project = (
            self.window.workspace
            .open_project(filename)
        )


        self.load_project_to_interface(
            project
        )



    ##################################################


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



    ##################################################


    def close_project(self):

        self.window.workspace.close_project()


        explorer = (
            self.window.dashboard
            .get_panel("explorer")
        )


        if explorer:

            explorer.clear()


        self.window.setWindowTitle(
            "Atmospheric Complexity Framework"
        )


        self.window.statusBar().showMessage(
            "Project closed"
        )



    ##################################################
    # DATA MANAGEMENT
    ##################################################

    def open_dataset(self):


        filename,_ = QFileDialog.getOpenFileName(
            self.window,
            "Open Scientific Dataset",
            "",
            """
            Meteorological files
            (*.grib *.grib2 *.grb *.nc *.nc4)
            """
        )


        if not filename:

            return



        try:


            dataset = (
                self.window.data
                .open(filename)
            )



            self.refresh_dataset_view()



            self.window.statusBar().showMessage(
                f"Dataset loaded : {dataset.name}"
            )



        except Exception as error:


            QMessageBox.critical(
                self.window,
                "Dataset Error",
                str(error)
            )



    ##################################################


    def close_dataset(self):

        self.window.data.close()



        self.window.statusBar().showMessage(
            "Dataset closed"
        )



    ##################################################


    def dataset_information(self):

        dataset = (
            self.window.data.current_dataset
        )


        if dataset is None:

            QMessageBox.information(
                self.window,
                "Dataset Information",
                "No dataset loaded."
            )

            return



        QMessageBox.information(
            self.window,
            "Dataset Information",
            str(
                dataset.summary()
            )
        )



    ##################################################


    def refresh_dataset_view(self):

        explorer = (
            self.window.dashboard
            .get_panel("explorer")
        )


        if explorer:

            explorer.refresh_datasets(
                self.window.data.datasets()
            )



    ##################################################
    # PROJECT PROPERTIES
    ##################################################

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



    ##################################################
    # LOAD PROJECT UI
    ##################################################

    def load_project_to_interface(
        self,
        project
    ):


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
    # RECENT
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

            action.setEnabled(
                False
            )

            self.recent_menu.addAction(
                action
            )

            return



        for item in projects:

            path = Path(item)

            action = QAction(
                path.parent.name,
                self.window
            )


            action.triggered.connect(
                lambda checked=False,
                file=item:
                self.open_project_file(file)
            )


            self.recent_menu.addAction(
                action
            )



    def open_project_file(self,filename):

        project = (
            self.window.workspace
            .open_project(filename)
        )

        self.load_project_to_interface(
            project
        )
