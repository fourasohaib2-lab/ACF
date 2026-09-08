"""
Atmospheric Complexity Framework (ACF)

Main Window (Compatibility Layer forwarding to acf.gui.main_window.main_window)

NOTE (found, NOT changed — RÈGLE D'OR / single source of truth): this
module is dead code, despite its own stated intent as a "Compatibility
Layer". `src/acf/gui/main_window/` is ALSO a package with its own
__init__.py, which Python's import resolution always finds before this
sibling module.py of the same name - so `import acf.gui.main_window`
can never actually reach this file's forwarding import; it always
resolves to the package's __init__.py instead. The real MainWindow
remains reachable directly via
`acf.gui.main_window.main_window.MainWindow` (or whatever the
package's own __init__.py re-exports). Not deleted per project
convention - flagged so nobody mistakes this for live code. Same
situation as data/engine.py's NOTE.
"""

from acf.gui.main_window.main_window import MainWindow

__all__ = ["MainWindow"]
