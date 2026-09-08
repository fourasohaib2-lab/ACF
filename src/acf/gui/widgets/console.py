"""
ACF Scientific Console
"""

from datetime import datetime

from PySide6.QtWidgets import QTextEdit


class ConsoleWidget(QTextEdit):
    """
    Console scientifique d'ACF.
    """

    def __init__(self):
        super().__init__()

        self.setReadOnly(True)

        self.setLineWrapMode(QTextEdit.NoWrap)

        self.setStyleSheet("""
            QTextEdit{
                background:#111111;
                color:#00FF7F;
                font-family:Consolas;
                font-size:11pt;
                border:none;
            }
        """)

        self.banner()

    ########################################################

    def banner(self):

        self.clear()

        self.append("=" * 70)
        self.append(" Atmospheric Complexity Framework")
        self.append(" Scientific Console")
        self.append("=" * 70)
        self.append("")

        self.info("Console initialized.")
        self.info("Ready.")

    ########################################################

    def timestamp(self):

        return datetime.now().strftime("%H:%M:%S")

    ########################################################

    def write(self, message):

        self.append(message)

    ########################################################

    def info(self, message):

        self.append(f"[{self.timestamp()}] [INFO] {message}")

    ########################################################

    def warning(self, message):

        self.append(f"[{self.timestamp()}] [WARNING] {message}")

    ########################################################

    def error(self, message):

        self.append(f"[{self.timestamp()}] [ERROR] {message}")

    ########################################################

    def success(self, message):

        self.append(f"[{self.timestamp()}] [SUCCESS] {message}")

    ########################################################

    def separator(self):

        self.append("-" * 70)
