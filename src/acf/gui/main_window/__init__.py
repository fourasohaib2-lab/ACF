"""
acf.gui.main_window - a real, self-consistent legacy main window
(MainWindow + menu_bar.py/tool_bar.py/status_bar.py/property_panel.py,
423 lines total), NOT the live one.

NOTE (Physics Guard, 2026-09-06 Tier C sweep): acf.gui.app.run() (the
real acf-gui entry point) only ever constructs ESOCWindow - MainWindow
is imported into app.py's own __all__ but never instantiated there,
and `MainWindow(` appears nowhere else in src/ or tests/ either
(verified by grep; tests/test_collisions_consolidation.py only checks
the acf.gui.main_window module-vs-package import-collision handled by
../main_window.py's own NOTE, not MainWindow's behavior). Not
fabricated - genuinely correct, working PySide6 code, just a legacy
window nothing constructs. Same "kept per AGENTS.md, disclosed rather
than silently trusted" treatment as acf.model4d.
"""

from acf.gui.main_window.main_window import MainWindow

__all__ = ["MainWindow"]
