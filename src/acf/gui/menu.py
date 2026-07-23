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

    def create(self):

        menu_bar = self.window.menuBar()


        file_menu = menu_bar.addMenu(
            "File"
        )


        menu_bar.addMenu("Edit")
        menu_bar.addMenu("View")
        menu_bar.addMenu("Data")
        menu_bar.addMenu("Tools")
        menu_bar.addMenu("Plugins")
        menu_bar.addMenu("Help")



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


        self.update_recent_projects()



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



    ##################################################

    def open_recent_project(self, filename):

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



    ##################################################

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



    ##################################################

    def show_project_properties(self):


        project = (
            self.window.workspace
            .project()
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


            self.window.statusBar().showMessage(
                "Project properties updated"
            )



    ##################################################

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


        self.window.statusBar().showMessage(
            "Project loaded"
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


        self.window.dashboard.clear_project()


        self.window.setWindowTitle(
            "Atmospheric Complexity Framework"
        )


        self.window.statusBar().showMessage(
            "No project opened."
        )
