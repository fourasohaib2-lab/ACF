from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QTextEdit,
    QVBoxLayout,
)


class PropertyPanel(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        title = QLabel("Properties")
        title.setStyleSheet("""
            font-size:16px;
            font-weight:bold;
        """)

        self.editor = QTextEdit()
        self.editor.setReadOnly(True)

        self.editor.setPlainText(
            "No object selected."
        )

        layout.addWidget(title)
        layout.addWidget(self.editor)

    def set_properties(self, text):
        self.editor.setPlainText(text)
