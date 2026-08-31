"""
Atmospheric Complexity Framework (ACF)

Utils helper test suite (paths, system, time, validators).

These 4 modules previously had 0% coverage - no test file imported
them at all. Trivial, correct implementations.
"""

import platform
from datetime import datetime
from pathlib import Path

from acf.utils import paths, system, time as acf_time, validators


def test_paths_are_relative_to_root():
    assert paths.ROOT.is_absolute()
    for sub in (paths.CONFIG, paths.LOGS, paths.CACHE, paths.WORKSPACE, paths.PLUGINS, paths.EXPORTS, paths.IMPORTS, paths.TEMP):
        assert sub.parent == paths.ROOT


def test_system_helpers():
    assert system.get_os_name() == platform.system()
    assert system.get_python_version() == platform.python_version()
    assert isinstance(system.get_project_root(), Path)
    assert system.get_project_root().is_absolute()


def test_time_helpers():
    before = datetime.now()
    result = acf_time.now()
    after = datetime.now()
    assert before <= result <= after

    ts = acf_time.timestamp()
    # Must parse back as "%Y-%m-%d %H:%M:%S"
    datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")


def test_validators(tmp_path):
    existing_file = tmp_path / "f.txt"
    existing_file.write_text("x")
    existing_dir = tmp_path / "d"
    existing_dir.mkdir()

    assert validators.is_existing_file(str(existing_file)) is True
    assert validators.is_existing_file(str(tmp_path / "missing.txt")) is False
    assert validators.is_existing_directory(str(existing_dir)) is True
    assert validators.is_existing_directory(str(tmp_path / "missing_dir")) is False
