"""
Tests for acf.gui.single_instance.SingleInstanceGuard - the fix for a
real user-reported bug ("plusieurs dashboard qui s'affiche au meme
temps" / several dashboards showing at once on launch): nothing
previously checked whether an ESOC instance was already running before
building a brand new, independent window.

Two SingleInstanceGuard instances sharing one QApplication event loop
(via qtbot's real Qt event processing) genuinely exercise the real
QLocalServer/QLocalSocket handshake - not a mock of it - using a
per-test unique server name so parallel test runs can't collide.
"""

from __future__ import annotations

import uuid

from acf.gui.single_instance import SingleInstanceGuard


def _unique_name() -> str:
    return f"acf-test-single-instance-{uuid.uuid4().hex}"


def test_first_instance_acquires_and_second_is_told_to_activate(qtbot):
    name = _unique_name()

    first = SingleInstanceGuard(server_name=name)
    assert first.acquire() is True

    activated = []
    first.activation_requested.connect(lambda: activated.append(True))

    second = SingleInstanceGuard(server_name=name)
    assert second.acquire() is False

    # The handshake is a real (if local) socket round-trip - give Qt's
    # event loop real time to deliver it, not an instant assertion.
    qtbot.waitUntil(lambda: len(activated) == 1, timeout=2000)


def test_a_third_instance_is_also_told_to_activate(qtbot):
    """Not just a one-shot: launching the app a 3rd, 4th... time must
    keep reaching the same first real instance, not silently stop
    coordinating after the first extra launch."""
    name = _unique_name()

    first = SingleInstanceGuard(server_name=name)
    assert first.acquire() is True

    activated = []
    first.activation_requested.connect(lambda: activated.append(True))

    second = SingleInstanceGuard(server_name=name)
    assert second.acquire() is False
    qtbot.waitUntil(lambda: len(activated) == 1, timeout=2000)

    third = SingleInstanceGuard(server_name=name)
    assert third.acquire() is False
    qtbot.waitUntil(lambda: len(activated) == 2, timeout=2000)


def test_after_the_first_instance_releases_a_new_one_can_acquire(qtbot):
    """A crashed/closed instance must not permanently block every
    future launch - once the real listener is actually gone, the next
    real launch must become the new first instance."""
    name = _unique_name()

    first = SingleInstanceGuard(server_name=name)
    assert first.acquire() is True

    # Simulate the first instance exiting: stop its server (this is
    # what a clean process exit does implicitly via Qt's own cleanup;
    # done explicitly here since the object is still alive in-process).
    assert first._server is not None
    first._server.close()

    second = SingleInstanceGuard(server_name=name)
    assert second.acquire() is True
