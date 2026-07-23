from PySide6.QtWidgets import QTextEdit

class PropertyPanel(QTextEdit):

    def __init__(self):
        super().__init__()

        self.setReadOnly(True)
        self.setPlainText("Properties")
