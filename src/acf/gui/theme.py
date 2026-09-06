"""
acf.gui.theme - ThemeManager, the real theme switcher.

Loads a .qss stylesheet file from gui/resources/themes/{name}.qss.
Genuinely used: acf.gui.app (initial theme) and
acf.gui.esoc.settings_dialog.SettingsDialog (live theme switching) -
verified by grep, not the module docstring template used elsewhere in
this package before its audit (no NumPy/scientific-engine dependency
here, pure stdlib pathlib).
"""

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
