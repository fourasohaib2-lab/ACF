"""
Atmospheric Complexity Framework (ACF)

acfctl - Health Report

Real environment/health report: whether each real, registered
console-script entry point is resolvable on ``PATH``, the real ACF
package version, the real Python version, the real running/stopped
status of each known app (``processes.status()``), and real free disk
space in the ``~/.acf`` local-state directory. Never a fabricated
"ALL SYSTEMS GO"-style self-certification - ``docs/STATUS.md`` itself
documents exactly that kind of fabricated claim being found and fixed
elsewhere in this codebase (``acf.gui.earth_system_operations``, a
module exported from ``gui/__init__.py`` and never actually built,
which returned a fabricated ``"ui_version": "ACF-UI-001 Production
Certified"``/``"integration_status": "ALL_45_MISSIONS_INTEGRATED"``
self-certification with no real UI behind it - corrected, per
``docs/STATUS.md``'s own Tier F entry), the cautionary precedent this
module is deliberately built to avoid repeating: every field here is a
real, independently-verifiable fact, never a synthesized "status: OK".
"""

from __future__ import annotations

import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

from tools.acfctl.apps import KNOWN_APPS
from tools.acfctl.processes import ProcessStatus, status as process_status


@dataclass(frozen=True)
class EntryPointStatus:
    """Real status of one known app's console-script entry point."""

    app: str
    console_script: str
    on_path: bool
    process: ProcessStatus


@dataclass(frozen=True)
class HealthReport:
    """Real, complete health report - every field independently
    verifiable, never a synthesized overall verdict."""

    acf_version: str
    python_version: str
    entry_points: tuple[EntryPointStatus, ...]
    free_disk_space_mb: float | None


def build_health_report() -> HealthReport:
    """Real health report for this ACF installation, built entirely
    from real, independently-checkable facts."""
    from acf.core.version import __version__ as acf_version

    entry_points = tuple(
        EntryPointStatus(
            app=app,
            console_script=console_script,
            on_path=shutil.which(console_script) is not None,
            process=process_status(app),
        )
        for app, console_script in sorted(KNOWN_APPS.items())
    )
    state_dir = Path.home() / ".acf"
    free_disk_space_mb: float | None
    try:
        usage_target = state_dir if state_dir.exists() else Path.home()
        free_disk_space_mb = shutil.disk_usage(usage_target).free / (1024 * 1024)
    except OSError:
        free_disk_space_mb = None
    return HealthReport(
        acf_version=acf_version,
        python_version=sys.version.split()[0],
        entry_points=entry_points,
        free_disk_space_mb=free_disk_space_mb,
    )


def format_health_report(report: HealthReport) -> str:
    """Real, human-readable rendering of ``report`` - one line per
    real, independently-verifiable fact."""
    lines = [
        f"ACF version: {report.acf_version}",
        f"Python version: {report.python_version}",
    ]
    for entry_point in report.entry_points:
        on_path = "on PATH" if entry_point.on_path else "NOT on PATH"
        running = f"running (pid {entry_point.process.pid})" if entry_point.process.running else "not running"
        lines.append(f"  {entry_point.app} ({entry_point.console_script}): {on_path}, {running}")
    if report.free_disk_space_mb is not None:
        lines.append(f"Free disk space (~/.acf): {report.free_disk_space_mb:.0f} MB")
    else:
        lines.append("Free disk space (~/.acf): not available")
    return "\n".join(lines)
