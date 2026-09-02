"""
CORRECTED: both tests here used to construct WorkspaceManager() with no
way to isolate its RecentProjectsManager, so create_project()/
save_project() wrote real entries into the actual user's
~/.acf/recent_projects.json on whatever machine ran this test suite -
confirmed present on disk from past runs. Now pass an isolated
recent_projects_file under pytest's own tmp_path.
"""

from acf.workspace.manager import WorkspaceManager


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
