"""Tests for the new AWCI workspace (src/awci/workspace/), built while
working through the full remaining-gaps list ("On les attaque toutes
un par un") after it was identified as the specific gap in
docs/architecture/acf_awci_architecture_gap_analysis.md ("No
AWCI-specific project/session format; ACF's own acf.workspace is
general-purpose").

AWCIProject/AWCIProjectSerializer/AWCIWorkspaceManager subclass the
already-real, already-working acf.workspace.* classes - these tests
focus on what is genuinely different (the .awciproj extension, the
AWCI_PROJECT_FOLDERS layout, the separate ~/.awci/recent_projects.json
default) and on the real save()/load() round-trip through the
subclassed types, following the same isolation discipline as
tests/test_workspace_manager.py (never touching the real user's
~/.acf or ~/.awci directories).
"""

from __future__ import annotations

from acf.workspace.project import Project
from awci.workspace import AWCI_PROJECT_FOLDERS, AWCIProject, AWCIProjectSerializer, AWCIWorkspaceManager


def test_create_project_uses_the_real_awci_folder_layout(tmp_path):
    manager = AWCIWorkspaceManager(recent_projects_file=tmp_path / "recent_projects.json")

    project = manager.create_project(name="RouteAudit", directory=tmp_path)

    assert project.name == "RouteAudit"
    assert isinstance(project, AWCIProject)
    for folder in AWCI_PROJECT_FOLDERS:
        assert (tmp_path / "RouteAudit" / folder).is_dir(), folder
    assert (tmp_path / "RouteAudit" / "RouteAudit.awciproj").exists()


def test_awci_project_folders_are_the_real_blueprint_set():
    assert AWCI_PROJECT_FOLDERS == (
        "data",
        "forecasts",
        "flights",
        "airports",
        "hazards",
        "maps",
        "reports",
        "analysis",
        "exports",
        "logs",
    )


def test_awci_project_file_uses_the_awciproj_extension_not_acfproj(tmp_path):
    manager = AWCIWorkspaceManager(recent_projects_file=tmp_path / "recent_projects.json")
    project = manager.create_project(name="Demo", directory=tmp_path)

    assert project.project_file.suffix == ".awciproj"
    assert not (tmp_path / "Demo" / "Demo.acfproj").exists()


def test_save_and_reopen_awci_project_preserves_state(tmp_path):
    manager = AWCIWorkspaceManager(recent_projects_file=tmp_path / "recent_projects.json")

    project = manager.create_project(name="Demo", directory=tmp_path)
    original_created = project.created
    project.datasets.append("kjfk_metar_2026.json")
    project.metadata["route"] = "KJFK-EGLL"
    project.settings["units"] = "metric"
    manager.save_project()

    reopened = manager.open_project(project.project_file)

    assert isinstance(reopened, AWCIProject)
    assert reopened.datasets == ["kjfk_metar_2026.json"]
    assert reopened.metadata == {"route": "KJFK-EGLL"}
    assert reopened.settings == {"units": "metric"}
    assert reopened.created == original_created


def test_renaming_an_awci_project_removes_the_stale_old_file(tmp_path):
    """Locks in the base ProjectSerializer.save()'s own real rename-
    cleanup fix still applies polymorphically to AWCIProject, since
    AWCIProjectSerializer.save reuses it unchanged."""
    manager = AWCIWorkspaceManager(recent_projects_file=tmp_path / "recent_projects.json")
    project = manager.create_project(name="Orig", directory=tmp_path)
    old_file = project.project_file
    assert old_file.exists()

    project.name = "Renamed"
    AWCIProjectSerializer.save(project)

    assert not old_file.exists()
    assert project.project_file.exists()
    assert project.project_file.name == "Renamed.awciproj"


def test_awci_recent_projects_defaults_to_a_separate_dot_awci_directory(monkeypatch, tmp_path):
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    monkeypatch.setattr("awci.workspace.manager.Path.home", lambda: fake_home)

    manager = AWCIWorkspaceManager()

    assert manager.recent.filename == fake_home / ".awci" / "recent_projects.json"


def test_awci_workspace_manager_reuses_base_lifecycle_methods_unchanged(tmp_path):
    """save_project/close_project/recent_projects/has_project/project/
    project_name/project_path are inherited, not redefined - this
    locks in they are the exact same real functions as the base
    WorkspaceManager's."""
    from acf.workspace.manager import WorkspaceManager

    for method_name in (
        "save_project",
        "close_project",
        "recent_projects",
        "has_project",
        "project",
        "project_name",
        "project_path",
    ):
        assert getattr(AWCIWorkspaceManager, method_name) is getattr(WorkspaceManager, method_name)


# --------------------------------------------------------------------- discipline


def test_awci_project_is_a_real_subclass_of_the_base_project_not_a_copy():
    assert issubclass(AWCIProject, Project)


def test_awci_project_serializer_reuses_the_base_save_method_not_a_copy():
    from acf.workspace.serializer import ProjectSerializer

    assert AWCIProjectSerializer.save is ProjectSerializer.save
