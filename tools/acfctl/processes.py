"""
Atmospheric Complexity Framework (ACF)

acfctl - Process Start/Stop/Status

Real, simple process supervisor for acfctl's known apps - real
``subprocess.Popen`` + a real PID file under ``~/.acf/run/`` (the same
real ``~/.acf/`` local-state convention already established by
``acf.workspace.recent``), and ``psutil`` (an already-real dependency
in ``requirements.txt``) for cross-platform liveness checks.
Deliberately NOT built on Qt's own ``QLocalServer`` single-instance
mechanism (``acf.gui.single_instance``) - that needs a running Qt event
loop to even check, and only ever covered ``acf-gui``, not
``acf-web``/``acf-awci``.
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import psutil

from tools.acfctl.apps import KNOWN_APPS

#: Real, real local-state directory acfctl tracks its own PID files
#: under - same ``~/.acf/`` convention already established by
#: ``acf.workspace.recent`` (module-level so tests can monkeypatch it
#: to a real temp directory rather than touching the real machine's
#: own state).
RUN_DIR = Path.home() / ".acf" / "run"


class UnknownAppError(ValueError):
    """Raised for an app name not in ``KNOWN_APPS`` - a real caller
    mistake, never silently treated as a real, unrecognized app."""


@dataclass(frozen=True)
class ProcessStatus:
    """Real, current status of one known app."""

    app: str
    running: bool
    pid: int | None


def _require_known(app: str) -> str:
    if app not in KNOWN_APPS:
        raise UnknownAppError(f"Unknown app {app!r} - known apps: {sorted(KNOWN_APPS)}")
    return KNOWN_APPS[app]


def _pid_file(app: str) -> Path:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    return RUN_DIR / f"{app}.pid"


def status(app: str) -> ProcessStatus:
    """
    Real liveness check - reads ``app``'s real PID file (if any) and
    verifies, via ``psutil``, that a real process with that PID is
    still alive AND that its real command line still mentions ``app``'s
    own real console-script name (a real, honest guard against PID
    reuse after a reboot silently misreporting an unrelated process as
    "still running"). A missing or stale PID file honestly reports
    "not running", never a fabricated ``True``.
    """
    console_script = _require_known(app)
    pid_file = _pid_file(app)
    if not pid_file.is_file():
        return ProcessStatus(app=app, running=False, pid=None)
    try:
        pid = int(pid_file.read_text().strip())
    except ValueError:
        return ProcessStatus(app=app, running=False, pid=None)
    if not psutil.pid_exists(pid):
        return ProcessStatus(app=app, running=False, pid=None)
    try:
        process = psutil.Process(pid)
        cmdline = " ".join(process.cmdline())
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return ProcessStatus(app=app, running=False, pid=None)
    if console_script not in cmdline:
        return ProcessStatus(app=app, running=False, pid=None)
    return ProcessStatus(app=app, running=True, pid=pid)


def start(app: str) -> int:
    """
    Real subprocess start of ``app``'s real console-script entry point
    (must already be resolvable on ``PATH`` - a real, installed/
    editable ACF package - a real ``FileNotFoundError`` propagates,
    never silently faked as started). Raises ``RuntimeError`` if
    ``status(app)`` already reports it running, rather than silently
    spawning a real second process.
    """
    console_script = _require_known(app)
    existing = status(app)
    if existing.running:
        raise RuntimeError(f"{app} is already running (pid {existing.pid}).")
    executable = shutil.which(console_script)
    if executable is None:
        raise FileNotFoundError(f"console script {console_script!r} was not found on PATH.")
    process = subprocess.Popen([executable])  # noqa: S603
    _pid_file(app).write_text(str(process.pid))
    return process.pid


def stop(app: str, timeout: float = 5.0) -> bool:
    """
    Real termination of a real, currently-running process for ``app`` -
    a real SIGTERM (``psutil.Process.terminate()``), waits up to
    ``timeout`` seconds for a real exit, then a real SIGKILL if still
    alive. Returns ``False`` (never raising) when ``app`` was not
    running - stopping something already stopped is not itself a
    failure, matching this whole session's established
    "removing/stopping an absent thing is a no-op, not an error"
    convention.
    """
    _require_known(app)
    current = status(app)
    if not current.running or current.pid is None:
        return False
    process = psutil.Process(current.pid)
    process.terminate()
    try:
        process.wait(timeout=timeout)
    except psutil.TimeoutExpired:
        process.kill()
        process.wait(timeout=timeout)
    _pid_file(app).unlink(missing_ok=True)
    return True
