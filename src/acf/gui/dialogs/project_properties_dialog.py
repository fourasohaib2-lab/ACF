"""
ACF Project Properties Dialog
"""

from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)


class ProjectPropertiesDialog(QDialog):
    """
    Fenêtre des propriétés du projet.
    """

    def __init__(self, project, parent=None):

        super().__init__(parent)

        self.project = project

        self.setWindowTitle("Project Properties")

        self.resize(500, 400)

        self.build_ui()

    ##################################################

    def build_ui(self):

        layout = QVBoxLayout()

        title = QLabel("ACF Project Information")

        layout.addWidget(title)

        form = QFormLayout()

        self.name_edit = QLineEdit(self.project.name)

        self.author_edit = QLineEdit(self.project.author)

        self.description_edit = QTextEdit(self.project.description)

        form.addRow("Name:", self.name_edit)

        form.addRow("Author:", self.author_edit)

        form.addRow("Description:", self.description_edit)

        layout.addLayout(form)

        save_button = QPushButton("Save")

        save_button.clicked.connect(self.accept)

        layout.addWidget(save_button)

        self.setLayout(layout)

    ##################################################

    def update_project(self):

        self.project.name = self.name_edit.text()

        self.project.author = self.author_edit.text()

        self.project.description = self.description_edit.toPlainText()
