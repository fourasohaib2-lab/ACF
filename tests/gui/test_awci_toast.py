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
    # Flush the toast's queued deleteLater BEFORE the test ends
    # (2026-09-09: intermittent native segfaults traced to the deferred
    # deletion instead executing inside pytest-qt's teardown/next-test
    # event processing, where host+toast are already being destroyed).
    # Deterministically drain the deleteLater queue here so teardown
    # never inherits it.
    from PySide6.QtCore import QCoreApplication, QEvent

    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    QCoreApplication.processEvents()


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


def test_dismiss_touching_a_toast_whose_cpp_object_died_does_not_crash(qtbot):
    """Real regression test for the 2026-09-09 `free(): invalid pointer`
    native crash found by the full GUI suite (position varies between
    runs, always inside pytest-qt's event processing after this file's
    auto-dismiss test): a toast's C++ object can die WITH its host in
    the same event-loop window the dismiss timer fires in - the
    context-object overload cancels only when the toast itself is
    gone BEFORE the timer, not when host and toast die together
    between timer setup and callback. _dismiss must therefore check
    shiboken validity before deleteLater() (and _reposition before
    touching any survivor) - without that guard this test aborts the
    process at the deleteLater() call.
    """
    host = QWidget()
    qtbot.addWidget(host)
    host.resize(800, 600)
    host.show()
    manager = AWCIToastManager(host)

    manager.show("Host dying with toast alive", kind="info", duration_ms=200)
    toast = manager._active[0]
    # Force exactly the state the crash ran into: wrapper alive in
    # Python, C++ object already destroyed (with the host).
    from shiboken6 import invalidate

    invalidate(toast)
    manager._dismiss(toast)  # must not raise OR touch the dead pointer

    assert manager._active == []
