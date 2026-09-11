"""
AWCI Toast Notifications
=========================

Non-blocking, auto-dismissing notification pills - a real 2026-style
replacement for the blocking `QMessageBox.information()`/`.warning()`
popups this dashboard used for routine, non-decision feedback (a
route applied, HPC connected, a file imported). A genuine decision the
operator must acknowledge (a real exception blocking a real action)
still uses QMessageBox - this widget is only for "something happened,
here is the honest result", not a substitute for every dialog.

AWCIToastManager is one instance per AWCIDashboard (`self._toasts`),
parented to the dashboard itself so it stacks correctly regardless of
which panel triggered it. Toasts appear bottom-right, stack upward,
and self-delete after a fixed duration - no manual cleanup required by
callers.

NOTE (correction, 2026-09-07 - real crash found by this session's own
full regression suite, not by any individual test): the first version
of this widget animated a QGraphicsOpacityEffect via QPropertyAnimation
for a fade in/out. Under real, repeated widget teardown (qtbot
destroying many hosts across many tests, or simply a real dashboard
window closing while a toast was still alive) this reliably crashed
the whole process - "pure virtual method called" / "terminate called
without an active exception" / Fatal Python error: Aborted - a known
class of Qt/PySide6 lifetime hazard: a QGraphicsEffect is not a
regular QObject child of the widget it's attached to in destruction
order, so a QPropertyAnimation still targeting it when the widget is
torn down can call into an already-destroyed C++ object. Fixed by
dropping the animated fade entirely - a toast now simply appears and
later self-deletes via `QTimer.singleShot(ms, toast, toast.deleteLater)`
(Qt's own context-object overload, which auto-cancels the call if
`toast` is destroyed first - no dangling callback either). Less showy
than a fade, but a real notification system that cannot crash the
application beats one that occasionally does.

Known, disclosed limitation: position is computed relative to the
dashboard widget's own top-level parent (`window()`), so a toast stays
pinned to the real visible window even while the dashboard scrolls -
except this dashboard's own real fix (2026-09-07, resolution-stability
work) means there is normally nothing to scroll on a real screen in
the first place.
"""

from __future__ import annotations

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget
from shiboken6 import isValid

from acf.gui.theme_tokens import TOKENS

#: severity -> (left-accent color, icon). Uses the shared TOKENS'
#: own success/warning/danger status colors (not ad hoc hex) - info
#: has no dedicated status token, so it reuses accent_primary, this
#: codebase's existing convention for a neutral informational accent.
_KINDS = {
    "success": (TOKENS.success, "✓"),
    "info": (TOKENS.accent_primary, "ℹ"),
    "warning": (TOKENS.warning, "⚠"),
    "error": (TOKENS.danger, "✕"),
}


class _AWCIToast(QFrame):
    def __init__(self, message: str, kind: str, parent: QWidget) -> None:
        super().__init__(parent)
        color, icon = _KINDS.get(kind, _KINDS["info"])
        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: {TOKENS.bg_surface};
                border: 1px solid {TOKENS.border};
                border-left: 3px solid {color};
                border-radius: 8px;
            }}
            """
        )
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"color: {color}; font-size: 13px; font-weight: bold; border: none;")
        layout.addWidget(icon_lbl)

        text_lbl = QLabel(message)
        text_lbl.setStyleSheet(f"color: {TOKENS.text_primary}; font-size: 11px; border: none;")
        text_lbl.setWordWrap(True)
        text_lbl.setMaximumWidth(340)
        layout.addWidget(text_lbl, stretch=1)

        self.setFixedWidth(360)
        self.adjustSize()


class AWCIToastManager:
    """Owns and positions every live toast for one AWCIDashboard."""

    def __init__(self, host: QWidget) -> None:
        self._host = host
        self._active: list[_AWCIToast] = []

    def show(self, message: str, kind: str = "info", duration_ms: int = 4000) -> None:
        toast = _AWCIToast(message, kind, self._host)
        self._active.append(toast)
        toast.show()
        toast.raise_()
        self._reposition()

        # Qt's context-object overload: the call is auto-cancelled if
        # `toast` is destroyed before duration_ms elapses (e.g. the
        # whole dashboard closing with a toast still up) - see this
        # module's own NOTE for the real crash this design avoids.
        QTimer.singleShot(duration_ms, toast, lambda: self._dismiss(toast))

    def _dismiss(self, toast: _AWCIToast) -> None:
        if toast not in self._active:
            return
        self._active.remove(toast)
        # Second lifetime guard (2026-09-09, real `free(): invalid
        # pointer` native crash found by the full GUI suite): the
        # context-object overload cancels the timer callback when the
        # toast's C++ object is destroyed, but nothing prevented
        # calling into a wrapper whose C++ part died WITH ITS HOST in
        # the same event-loop window (host torn down between the
        # singleShot firing and this running). isValid() is the
        # canonical shiboken guard for exactly that state - a dead
        # C++ object needs no deleteLater, and touching it is the
        # crash itself.
        if isValid(toast):
            toast.deleteLater()
        self._reposition()

    def _reposition(self) -> None:
        # Drop wrappers whose C++ objects died with a destroyed host
        # before repositioning the survivors - same guard as _dismiss.
        self._active = [toast for toast in self._active if isValid(toast)]
        top_level = self._host.window()
        if not isValid(top_level):
            return
        margin = 16
        y = top_level.height() - margin
        for toast in reversed(self._active):
            toast.resize(toast.sizeHint())
            y -= toast.height()
            x = top_level.width() - toast.width() - margin
            # Real coordinate conversion (top_level's local (x, y) ->
            # self._host's local space) via the global position, not a
            # manual offset guess - correct regardless of how deeply
            # self._host is nested inside top_level's own layout.
            global_pos = top_level.mapToGlobal(top_level.rect().topLeft())
            host_origin = self._host.mapFromGlobal(global_pos)
            toast.move(x + host_origin.x(), y + host_origin.y())
            y -= 8
