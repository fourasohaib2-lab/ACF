from pathlib import Path

class ThemeManager:

    def __init__(self):
        self.theme = "dark"

    def stylesheet(self):

        root = Path(__file__).parent

        file = root / "resources" / "themes" / f"{self.theme}.qss"

        return file.read_text(encoding="utf-8")

    def set_theme(self, name):

        self.theme = name
