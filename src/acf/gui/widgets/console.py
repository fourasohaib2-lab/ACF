from PySide6.QtWidgets import QTextEdit

class ConsoleWidget(QTextEdit):

    def __init__(self):
        super().__init__()

        self.setReadOnly(True)
        self.append("ACF Console Ready")
