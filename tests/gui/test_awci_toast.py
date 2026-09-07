"""
Tests for AWCIToastManager - the real, non-blocking notification system
added 2026-09-07 ("rends-le exceptionnel" 2026-modernization pass) to
replace routine QMessageBox popups (route applied, HPC connected/
disconnected, model file imported) with auto-dismissing toasts.

Includes the regression test for a real bug found (and fixed) while
building this: QTimer.singleShot()'s dismiss callback had no lifetime
tie to the toast widget - a toast still pending dismissal when its
host is destroyed raised RuntimeError ("Signal source has been
deleted"), the same class of GC/lifetime race already found and fixed
once this session for _HPCConnectWorker.
"""

from __future__ import annotations

from PySide6.QtWidgets import QWidget

from acf.gui.dashboard.awci_toast import AWCIToastManager


def test_showing_a_toast_creates_one_visible_active_widget(qtbot):
    host = QWidget()
    qtbot.addWidget(host)
    host.resize(800, 600)
    host.show()
    manager = AWCIToastManager(host)

    manager.show("Route applied", kind="success")

    assert len(manager._active) == 1
    assert manager._active[0].isVisible() is True


def test_multiple_toasts_stack_without_overlapping(qtbot):
    host = QWidget()
    qtbot.addWidget(host)
    host.resize(800, 600)
    host.show()
    manager = AWCIToastManager(host)

    manager.show("First", kind="info")
    manager.show("Second", kind="warning")

    assert len(manager._active) == 2
    y_positions = [toast.y() for toast in manager._active]
    assert y_positions[0] != y_positions[1]  # genuinely stacked, not drawn on top of each other


def test_a_toast_auto_dismisses_after_its_real_duration(qtbot):
    host = QWidget()
    qtbot.addWidget(host)
    host.resize(800, 600)
    host.show()
    manager = AWCIToastManager(host)

    manager.show("Disconnected from HPC", kind="info", duration_ms=50)

    qtbot.waitUntil(lambda: len(manager._active) == 0, timeout=2000)


def test_destroying_the_host_while_a_toast_is_still_pending_does_not_raise(qtbot):
    """The real regression test for the QTimer.singleShot lifetime bug
    - see this module's own docstring for the exact failure this
    reproduces without the fix (toast's dismiss context tied to
    `toast` itself, not a bare lambda)."""
    host = QWidget()
    qtbot.addWidget(host)
    host.resize(800, 600)
    host.show()
    manager = AWCIToastManager(host)

    manager.show("Connected to FENNEC", kind="success", duration_ms=100)
    host.deleteLater()
    qtbot.wait(50)  # host destroyed before the 100ms dismissal fires

    # No exception should propagate from the pending singleShot -
    # qtbot.wait() itself already pumps the event loop where a
    # dangling callback would have raised.
    qtbot.wait(150)
