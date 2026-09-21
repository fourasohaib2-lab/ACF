"""Tests for the new acfctl operational control point (tools/acfctl/),
built while working through the full remaining-gaps list ("On les
attaque toutes un par un") after it was identified as a genuinely
absent piece in docs/architecture/acf_awci_architecture_gap_analysis.md
("tools/acfctl/ ... was not found... acfctl start/stop/status/report
does not exist").

Real process supervision (subprocess.Popen + psutil liveness checks,
not a fabricated status), real environment/health reporting (every
field independently verifiable, never a synthesized "status: OK" -
see report.py's own docstring for the disclosed
earth_system_operations.py cautionary precedent). Real start/stop
tests use a real, lightweight fake executable (never the actual heavy
acf-gui/acf-web/acf-awci apps, which need a real display/network) so
these tests stay fast and hermetic.
"""

from __future__ import annotations

import shutil
import stat
import sys
import time
import tomllib
from pathlib import Path

import pytest

from tools.acfctl import cli, report
from tools.acfctl.apps import KNOWN_APPS
from tools.acfctl.processes import ProcessStatus, UnknownAppError
from tools.acfctl.processes import start as start_app
from tools.acfctl.processes import status as status_app
from tools.acfctl.processes import stop as stop_app

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture()
def isolated_run_dir(tmp_path, monkeypatch):
    """Redirects RUN_DIR to a real temp directory so tests never touch
    the real machine's own ~/.acf/run/."""
    import tools.acfctl.processes as processes_module

    run_dir = tmp_path / "run"
    monkeypatch.setattr(processes_module, "RUN_DIR", run_dir)
    return run_dir


@pytest.fixture()
def fake_gui_executable(tmp_path):
    """A real, lightweight, long-running fake 'acf-gui' executable -
    a real OS process the tests can actually start/stop, never the
    heavy real acf-gui (which needs a real display)."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake_exe = bin_dir / "acf-gui"
    fake_exe.write_text(f"#!{sys.executable}\nimport time\ntime.sleep(30)\n")
    fake_exe.chmod(fake_exe.stat().st_mode | stat.S_IEXEC)
    return bin_dir


# --------------------------------------------------------------------- apps


def test_known_apps_matches_pyproject_scripts_exactly():
    """KNOWN_APPS must never silently drift from the real, already-
    registered [project.scripts] table."""
    with open(REPO_ROOT / "pyproject.toml", "rb") as handle:
        pyproject = tomllib.load(handle)
    real_scripts = set(pyproject["project"]["scripts"])
    assert set(KNOWN_APPS.values()) <= real_scripts
    assert real_scripts == {"acf-gui", "acf-web", "acf-awci"}
    assert set(KNOWN_APPS.values()) == real_scripts


def test_known_apps_has_the_three_real_short_names():
    assert set(KNOWN_APPS) == {"gui", "web", "awci"}


# --------------------------------------------------------------------- processes.status


def test_status_of_an_app_with_no_pid_file_is_honestly_not_running(isolated_run_dir):
    current = status_app("gui")
    assert current == ProcessStatus(app="gui", running=False, pid=None)


def test_status_rejects_an_unknown_app(isolated_run_dir):
    with pytest.raises(UnknownAppError):
        status_app("not-a-real-app")


def test_status_with_a_stale_pid_file_reports_not_running(isolated_run_dir):
    isolated_run_dir.mkdir(parents=True, exist_ok=True)
    # A real PID essentially guaranteed not to correspond to a real,
    # currently-running acf-gui process.
    (isolated_run_dir / "gui.pid").write_text("999999999")
    current = status_app("gui")
    assert current.running is False
    assert current.pid is None


def test_status_with_a_corrupt_pid_file_is_honestly_not_running(isolated_run_dir):
    isolated_run_dir.mkdir(parents=True, exist_ok=True)
    (isolated_run_dir / "gui.pid").write_text("not-a-real-pid")
    current = status_app("gui")
    assert current.running is False


def test_status_detects_pid_reuse_by_a_real_unrelated_process(isolated_run_dir):
    """A real, currently-alive process whose cmdline does NOT mention
    the known app's own console-script name must be honestly reported
    as not running - never a fabricated 'running' from PID reuse."""
    import subprocess

    process = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
    try:
        isolated_run_dir.mkdir(parents=True, exist_ok=True)
        (isolated_run_dir / "gui.pid").write_text(str(process.pid))
        current = status_app("gui")
        assert current.running is False
    finally:
        process.terminate()
        process.wait(timeout=5)


# --------------------------------------------------------------------- processes.start/stop


def test_start_stop_real_lifecycle(isolated_run_dir, fake_gui_executable, monkeypatch):
    monkeypatch.setenv("PATH", f"{fake_gui_executable}:{shutil.os.environ['PATH']}")
    assert status_app("gui").running is False

    pid = start_app("gui")
    assert pid > 0
    time.sleep(0.3)
    current = status_app("gui")
    assert current.running is True
    assert current.pid == pid

    stopped = stop_app("gui")
    assert stopped is True
    time.sleep(0.3)
    assert status_app("gui").running is False


def test_start_raises_when_already_running(isolated_run_dir, fake_gui_executable, monkeypatch):
    monkeypatch.setenv("PATH", f"{fake_gui_executable}:{shutil.os.environ['PATH']}")
    start_app("gui")
    time.sleep(0.3)
    try:
        with pytest.raises(RuntimeError):
            start_app("gui")
    finally:
        stop_app("gui")


def test_start_raises_file_not_found_when_executable_is_missing(isolated_run_dir, monkeypatch, tmp_path):
    empty_bin = tmp_path / "empty-bin"
    empty_bin.mkdir()
    monkeypatch.setenv("PATH", str(empty_bin))
    with pytest.raises(FileNotFoundError):
        start_app("gui")


def test_stop_on_a_non_running_app_returns_false_never_raises(isolated_run_dir):
    assert stop_app("gui") is False


def test_start_rejects_an_unknown_app(isolated_run_dir):
    with pytest.raises(UnknownAppError):
        start_app("not-a-real-app")


# --------------------------------------------------------------------- report


def test_build_health_report_has_real_independently_verifiable_fields():
    health = report.build_health_report()
    assert health.acf_version != ""
    assert health.python_version == sys.version.split()[0]
    assert {ep.app for ep in health.entry_points} == set(KNOWN_APPS)
    for entry_point in health.entry_points:
        assert entry_point.console_script == KNOWN_APPS[entry_point.app]


def test_format_health_report_includes_every_entry_point():
    health = report.build_health_report()
    text = report.format_health_report(health)
    for console_script in KNOWN_APPS.values():
        assert console_script in text
    assert "ACF version:" in text
    assert "Python version:" in text


def test_health_report_never_claims_a_synthesized_overall_status():
    """No fabricated 'status: OK'/'ALL SYSTEMS GO'-style field exists
    anywhere on HealthReport - every field is independently checkable."""
    health = report.build_health_report()
    field_names = {f for f in health.__dataclass_fields__}
    assert "status" not in field_names
    assert "overall_status" not in field_names
    assert "certified" not in field_names


# --------------------------------------------------------------------- cli


def test_cli_report_command_runs_and_prints(capsys):
    exit_code = cli.main(["report"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "ACF version:" in captured.out


def test_cli_status_command_for_a_non_running_app(isolated_run_dir, capsys):
    exit_code = cli.main(["status", "gui"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "gui: not running" in captured.out


def test_cli_rejects_an_unknown_app_at_the_argparse_level():
    with pytest.raises(SystemExit):
        cli.main(["status", "not-a-real-app"])


def test_cli_requires_a_command():
    with pytest.raises(SystemExit):
        cli.main([])


def test_cli_start_stop_full_lifecycle(isolated_run_dir, fake_gui_executable, monkeypatch, capsys):
    monkeypatch.setenv("PATH", f"{fake_gui_executable}:{shutil.os.environ['PATH']}")
    start_code = cli.main(["start", "gui"])
    assert start_code == 0
    assert "started (pid" in capsys.readouterr().out
    time.sleep(0.3)

    status_code = cli.main(["status", "gui"])
    assert status_code == 0
    assert "running (pid" in capsys.readouterr().out

    stop_code = cli.main(["stop", "gui"])
    assert stop_code == 0
    assert "gui stopped." in capsys.readouterr().out


def test_cli_start_reports_a_real_error_on_stderr_not_a_traceback(isolated_run_dir, monkeypatch, tmp_path, capsys):
    empty_bin = tmp_path / "empty-bin"
    empty_bin.mkdir()
    monkeypatch.setenv("PATH", str(empty_bin))
    exit_code = cli.main(["start", "gui"])
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "acfctl:" in captured.err


def test_build_parser_exposes_the_four_real_commands():
    parser = cli.build_parser()
    subparsers_action = next(a for a in parser._actions if a.dest == "command")
    assert set(subparsers_action.choices) == {"start", "stop", "status", "report"}
