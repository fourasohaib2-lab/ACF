"""
CORRECTED: both tests here used to construct WorkspaceManager() with no
way to isolate its RecentProjectsManager, so create_project()/
save_project() wrote real entries into the actual user's
~/.acf/recent_projects.json on whatever machine ran this test suite -
confirmed present on disk from past runs. Now pass an isolated
recent_projects_file under pytest's own tmp_path.
"""

import logging

from acf.workspace.manager import WorkspaceManager
from acf.workspace.recent import RecentProjectsManager


def test_create_project(tmp_path):

    manager = WorkspaceManager(recent_projects_file=tmp_path / "recent_projects.json")

    project = manager.create_project(
        name="Demo",
        directory=tmp_path,
    )

    assert project.name == "Demo"

    assert (tmp_path / "Demo").exists()

    assert (tmp_path / "Demo" / "data").exists()

    assert (tmp_path / "Demo" / "Demo.acfproj").exists()


def test_save_and_reopen_project_preserves_state(tmp_path):
    """
    CORRECTED: Project.to_dict()/from_dict() used to silently drop
    datasets/maps/models/reports/scripts/plugins entirely and
    metadata/settings/created even when present in the saved JSON -
    every save()+open() round-trip (the only persistence path
    WorkspaceManager uses) discarded a project's resources, metadata,
    settings, and original creation date.
    """
    manager = WorkspaceManager(recent_projects_file=tmp_path / "recent_projects.json")

    project = manager.create_project(name="Demo", directory=tmp_path)
    original_created = project.created
    project.datasets.append("era5_2024.nc")
    project.metadata["region"] = "north_africa"
    project.settings["units"] = "metric"
    manager.save_project()

    reopened = manager.open_project(project.project_file)

    assert reopened.datasets == ["era5_2024.nc"]
    assert reopened.metadata == {"region": "north_africa"}
    assert reopened.settings == {"units": "metric"}
    assert reopened.created == original_created


def test_recent_projects_manager_logs_and_recovers_from_a_corrupted_file(tmp_path, caplog):
    """
    Regression guard (2026-09-05, post-model4d audit): load() used to
    have a bare `except Exception: pass`, silently treating a present
    but corrupted recent_projects.json identically to "no file yet" -
    no log at all, and the next save() would overwrite the corrupted
    file with an empty list. Must now log a real warning and still
    recover to an empty (not crashed) state.
    """
    recent_file = tmp_path / "recent_projects.json"
    recent_file.write_text("{not valid json", encoding="utf-8")

    with caplog.at_level(logging.WARNING):
        manager = RecentProjectsManager(filename=recent_file)

    assert manager.projects == []
    assert any("Failed to load recent projects" in record.message for record in caplog.records)
