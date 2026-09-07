"""
Tests for acf.awci_app - the standalone AWCI launcher (explicit user
request: "une vraie application séparée... pas juste une 2e fenêtre Qt
dans le même processus"). Genuinely independent from acf.gui.app
(ESOC): own QApplication, own process, own SingleInstanceGuard server
name.

run()'s real happy path ends in `sys.exit(app.exec())`, which blocks
forever - not callable directly in a test (same reason acf.gui.app.run()
itself has no direct test either). The --version/--help early-return
paths are safe (they return before touching Qt at all) and are tested
directly; the real end-to-end process behavior (launch, second-instance
detection, clean exit) was verified once by hand with two real
`acf-awci` processes - see this module's own docstring and
tests/test_esoc_launch_awci_app_action.py's own docstring for that
methodology.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from acf import __version__
from acf.awci_app import _AWCI_APP_SERVER_NAME
from acf.gui.single_instance import SERVER_NAME as ESOC_SERVER_NAME


def test_version_flag_prints_and_returns_without_touching_qt(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["acf-awci", "--version"])

    from acf.awci_app import run

    run()

    captured = capsys.readouterr()
    assert "AWCI" in captured.out
    assert __version__ in captured.out


def test_help_flag_prints_usage_and_returns(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["acf-awci", "--help"])

    from acf.awci_app import run

    run()

    captured = capsys.readouterr()
    assert "Usage: acf-awci" in captured.out


def test_server_name_is_distinct_from_esocs_own():
    """The whole safety property this app's single-instance guard
    depends on: a real ESOC instance and a real acf-awci instance
    running at the same time must never be mistaken for each other -
    confirmed by construction (different server name), not by
    assumption."""
    assert _AWCI_APP_SERVER_NAME != ESOC_SERVER_NAME


def test_console_script_is_installed_and_reports_its_own_version():
    """Real, installed console script (pyproject.toml's
    [project.scripts] acf-awci = "acf.awci_app:main"), not just an
    importable module - confirmed by actually running it as a real
    subprocess, the same way a user would from a terminal. Located next
    to sys.executable (this venv's own bin/) rather than assumed to be
    on PATH - a test process invoked as `.venv/bin/python -m pytest`
    (this project's own convention, see docs/STATUS.md) has no
    guarantee its shell PATH includes .venv/bin at all."""
    script = Path(sys.executable).parent / "acf-awci"
    assert script.exists(), f"console script not installed at {script}"

    result = subprocess.run(
        [str(script), "--version"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0
    assert "AWCI" in result.stdout
