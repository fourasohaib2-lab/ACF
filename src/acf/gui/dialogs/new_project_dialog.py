"""
New Project Dialog
"""

from pathlib import Path

from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)


class NewProjectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("New Project")
        self.setMinimumWidth(600)

        layout = QVBoxLayout(self)

        # -------------------------
        # Nom
        # -------------------------

        layout.addWidget(QLabel("Project name"))

        self.name_edit = QLineEdit()

        layout.addWidget(self.name_edit)

        # -------------------------
        # Auteur
        # -------------------------

        layout.addWidget(QLabel("Author"))

        self.author_edit = QLineEdit()

        layout.addWidget(self.author_edit)

        # -------------------------
        # Description
        # -------------------------

        layout.addWidget(QLabel("Description"))

        self.description_edit = QTextEdit()

        self.description_edit.setMaximumHeight(100)

        layout.addWidget(self.description_edit)

        # -------------------------
        # Dossier
        # -------------------------

        layout.addWidget(QLabel("Location"))

        path_layout = QHBoxLayout()

        self.path_edit = QLineEdit(str(Path.home()))

        browse_button = QPushButton("Browse...")

        browse_button.clicked.connect(self.select_directory)

        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(browse_button)

        layout.addLayout(path_layout)

        # -------------------------
        # Boutons
        # -------------------------

        buttons = QHBoxLayout()

        cancel = QPushButton("Cancel")
        create = QPushButton("Create")

        cancel.clicked.connect(self.reject)
        create.clicked.connect(self.validate)

        buttons.addStretch()
        buttons.addWidget(cancel)
        buttons.addWidget(create)

        layout.addLayout(buttons)

    # =====================================================

    def select_directory(self):

        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Project Folder",
            self.path_edit.text(),
        )

        if folder:
            self.path_edit.setText(folder)

    # =====================================================

    def validate(self):

        if not self.name_edit.text().strip():
            QMessageBox.warning(
                self,
                "Missing name",
                "Please enter a project name.",
            )

            return

        self.accept()

    # =====================================================

    def project_data(self):

        return {
            "name": self.name_edit.text().strip(),
            "author": self.author_edit.text().strip(),
            "description": self.description_edit.toPlainText().strip(),
            "directory": self.path_edit.text().strip(),
        }
