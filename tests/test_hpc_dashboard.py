"""
Unit test suite for ACF HPC Dashboard Backend (ACF-HPC-003).
"""

import json
from pathlib import Path

from acf.hpc_connector import HPCDashboard
from acf.hpc_connector.hpc_monitor import HPCMonitor


def test_hpc_dashboard_refresh_and_summary():
    """Test HPCDashboard refresh and summary methods."""
    dashboard = HPCDashboard()
    summary = dashboard.refresh()

    assert "timestamp" in summary
    assert "cluster_health" in summary
    assert "health_score" in summary
    assert summary["cluster_health"]["scheduler"] == "slurm"

    cached_summary = dashboard.summary()
    assert cached_summary["timestamp"] == summary["timestamp"]


def test_hpc_dashboard_health_score():
    """Test HPCDashboard health_score calculation."""
    dashboard = HPCDashboard()
    score = dashboard.health_score()
    assert 0.0 <= score <= 100.0


def test_hpc_dashboard_export_json(tmp_path: Path):
    """Test export_json to string and file."""
    dashboard = HPCDashboard()
    out_file = tmp_path / "hpc_status.json"

    json_str = dashboard.export_json(filepath=str(out_file))
    assert isinstance(json_str, str)
    assert out_file.exists()

    loaded = json.loads(out_file.read_text(encoding="utf-8"))
    assert loaded["cluster_health"]["scheduler"] == "slurm"


def test_hpc_dashboard_health_score_does_not_crash_when_fully_disconnected():
    """
    CORRECTED: health_score() used to call cpu.get("cpu_load_pct", 50.0)
    - a fabricated default that masked HPCMonitor having no real CPU
    data. Once HPCMonitor was fixed to honestly report cpu_load_pct=None
    when disconnected (no real scheduler backend - see
    hpc_monitor.py's NOTE (correction)), this crashed with
    `TypeError: '>' not supported between instances of 'NoneType' and 'float'`.
    Now skips the CPU-load penalty gracefully instead of crashing or
    fabricating an assumed load.
    """

    class AlwaysEmptyExecutor:
        def execute_command(self, cmd: str) -> str:
            return ""

    monitor = HPCMonitor(remote_executor=AlwaysEmptyExecutor())
    dashboard = HPCDashboard(monitor=monitor)

    score = dashboard.health_score()
    assert 0.0 <= score <= 100.0

    summary = dashboard.refresh()
    assert summary["cluster_health"]["connected"] is False
    assert summary["cpu"]["cpu_load_pct"] is None
