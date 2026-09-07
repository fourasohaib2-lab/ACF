"""
Tests for ESOCWindow's "🚀 AWCI (App)" toolbar action - explicit user
request ("une vraie application séparée... pas juste une 2e fenêtre Qt
dans le même processus"): unlike the existing "✈️ AWCI" action (see
tests/test_esoc_awci_field.py), which opens AWCIDashboardWindow as a
second window inside ESOC's own process, this spawns acf.awci_app as a
genuinely independent OS process via subprocess.Popen.

subprocess.Popen is mocked throughout - a real test run must not
actually spawn a real GUI process (slow, leaves a real window/process
behind, and not what "does _launch_awci_app() call the right thing
correctly" needs to prove). The real subprocess launch itself is
verified separately, once, by hand (two real `acf-awci` processes
launched: the first stayed alive, the second detected it via the real
single-instance guard and exited cleanly - the same real-process
methodology already used for acf-gui's own single-instance guard).
"""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

from acf.gui.esoc.esoc_toolbar import ESOCToolbar
from acf.gui.esoc.esoc_window import ESOCWindow


def test_toolbar_has_the_real_launch_awci_app_action(qtbot):
    toolbar = ESOCToolbar()
    qtbot.addWidget(toolbar)
    action_labels = [act.text() for act in toolbar.actions()]
    assert "🚀 AWCI (App)" in action_labels
    # Distinct from, not a replacement for, the existing in-process one.
    assert "✈️ AWCI" in action_labels


def test_launch_awci_app_spawns_the_real_module_as_a_subprocess(qtbot):
    win = ESOCWindow()
    qtbot.addWidget(win)

    with patch("subprocess.Popen") as mock_popen:
        mock_popen.return_value = MagicMock()
        win._launch_awci_app()

    mock_popen.assert_called_once_with([sys.executable, "-m", "acf.awci_app"])


def test_launch_awci_app_does_not_create_any_in_process_window(qtbot):
    """The whole point: this must NOT touch ESOCWindow's own
    _awci_dashboard_window (that's _open_awci_dashboard()'s job) -
    a real separate process, not a second window in this one."""
    win = ESOCWindow()
    qtbot.addWidget(win)
    assert win._awci_dashboard_window is None

    with patch("subprocess.Popen") as mock_popen:
        mock_popen.return_value = MagicMock()
        win._launch_awci_app()

    assert win._awci_dashboard_window is None


def test_launch_awci_app_reports_a_launch_failure_honestly_instead_of_raising(qtbot):
    win = ESOCWindow()
    qtbot.addWidget(win)
    messages = []
    win.dispatcher.log_message_emitted.connect(lambda level, msg: messages.append((level, msg)))

    with patch("subprocess.Popen", side_effect=OSError("python interpreter not found")):
        win._launch_awci_app()  # must not raise

    assert any(level == "ERROR" and "Failed to launch AWCI app" in msg for level, msg in messages)


def test_toolbar_action_dispatch_reaches_the_real_handler(qtbot):
    win = ESOCWindow()
    qtbot.addWidget(win)

    with patch("subprocess.Popen") as mock_popen:
        mock_popen.return_value = MagicMock()
        win._handle_toolbar_action("launch_awci_app")

    mock_popen.assert_called_once_with([sys.executable, "-m", "acf.awci_app"])
