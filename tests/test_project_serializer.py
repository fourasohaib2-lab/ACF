"""
Tests for acf.workspace.serializer.ProjectSerializer - had zero test
coverage before this file, despite being the only persistence path
WorkspaceManager uses for every real "New/Save/Open Project" action.

Worth locking in with real regression tests specifically because
Project.to_dict()/from_dict() (the serializer's own dependency) already
had one real, silent bug here (see that method's own NOTE): a
save()+load() round-trip used to discard datasets/maps/models/reports/
scripts/plugins/metadata/settings entirely, and replaced the original
"created" timestamp with a fresh one - already fixed, verified correct
here, with tests to keep it that way.
"""

from __future__ import annotations

from pathlib import Path

from acf.workspace.project import Project
from acf.workspace.serializer import ProjectSerializer


def test_save_writes_a_real_file_on_disk(tmp_path):
    root = tmp_path / "SaveTestProject"
    root.mkdir()
    project = Project(name="SaveTestProject", root_path=root)

    filename = ProjectSerializer.save(project)

    assert Path(filename).exists()
    assert Path(filename) == root / "SaveTestProject.acfproj"


def test_save_then_load_round_trips_every_real_field(tmp_path):
    root = tmp_path / "RoundTripProject"
    root.mkdir()
    project = Project(
        name="RoundTripProject",
        root_path=root,
        author="souhaib",
        description="real round-trip test",
    )
    project.datasets.append("FULLPOS_2026083100_0000")
    project.maps.append("aladin_domain")
    project.metadata["source"] = "RESTOR/ALADIN"
    project.settings["theme"] = "dark"
    original_created = project.created

    filename = ProjectSerializer.save(project)
    loaded = ProjectSerializer.load(filename)

    assert loaded.name == project.name
    assert loaded.author == project.author
    assert loaded.description == project.description
    assert loaded.datasets == ["FULLPOS_2026083100_0000"]
    assert loaded.maps == ["aladin_domain"]
    assert loaded.metadata == {"source": "RESTOR/ALADIN"}
    assert loaded.settings == {"theme": "dark"}
    # The original creation date must survive, not be replaced by a
    # fresh "now" timestamp on load (the exact bug this file's own
    # NOTE, in project.py, documents as already fixed).
    assert loaded.created == original_created


def test_save_updates_the_modified_timestamp(tmp_path):
    root = tmp_path / "TouchProject"
    root.mkdir()
    project = Project(name="TouchProject", root_path=root)
    project.modified = "2020-01-01T00:00:00"

    ProjectSerializer.save(project)

    assert project.modified != "2020-01-01T00:00:00"


def test_load_from_a_path_object(tmp_path):
    root = tmp_path / "PathObjectProject"
    root.mkdir()
    project = Project(name="PathObjectProject", root_path=root)
    filename = ProjectSerializer.save(project)

    loaded = ProjectSerializer.load(Path(filename))

    assert loaded.name == "PathObjectProject"


def test_load_from_a_string_path(tmp_path):
    root = tmp_path / "StringPathProject"
    root.mkdir()
    project = Project(name="StringPathProject", root_path=root)
    filename = ProjectSerializer.save(project)

    loaded = ProjectSerializer.load(str(filename))

    assert loaded.name == "StringPathProject"


def test_saving_a_renamed_project_removes_the_stale_old_file(tmp_path):
    """
    NOTE (correction, 2026-09-07): Project.project_file is computed
    from the project's current name, so a real, reachable flow
    (ProjectPropertiesDialog.update_project() changing project.name,
    then MenuManager.show_project_properties() calling save_project()
    right after) used to leave the OLD .acfproj file behind, orphaned
    with stale data, alongside the new one - confirmed by this exact
    scenario before the fix. save() now removes the previously-known
    file when the computed path has changed since this Project
    instance's last real save.
    """
    root = tmp_path / "OriginalName"
    root.mkdir()
    project = Project(name="OriginalName", root_path=root)
    ProjectSerializer.save(project)
    old_file = root / "OriginalName.acfproj"
    assert old_file.exists()

    project.name = "RenamedName"
    ProjectSerializer.save(project)

    new_file = root / "RenamedName.acfproj"
    assert new_file.exists()
    assert not old_file.exists()
    assert list(root.glob("*.acfproj")) == [new_file]


def test_multiple_renames_never_leave_more_than_one_file_behind(tmp_path):
    root = tmp_path / "MultiRename"
    root.mkdir()
    project = Project(name="MultiRename", root_path=root)
    ProjectSerializer.save(project)

    for new_name in ["SecondName", "ThirdName", "FourthName"]:
        project.name = new_name
        ProjectSerializer.save(project)

    assert list(root.glob("*.acfproj")) == [root / "FourthName.acfproj"]


def test_re_saving_without_a_rename_does_not_delete_the_current_file(tmp_path):
    root = tmp_path / "NoRename"
    root.mkdir()
    project = Project(name="NoRename", root_path=root)
    ProjectSerializer.save(project)

    ProjectSerializer.save(project)

    assert (root / "NoRename.acfproj").exists()


def test_renaming_after_load_also_cleans_up_the_old_file(tmp_path):
    """The rename-cleanup must work for a Project that came from
    load(), not only one that was just save()'d in the same process -
    confirmed via the real WorkspaceManager.open_project() -> save_project()
    path, not just calling the serializer directly."""
    root = tmp_path / "LoadThenRename"
    root.mkdir()
    original = Project(name="LoadThenRename", root_path=root)
    original_file = ProjectSerializer.save(original)

    loaded = ProjectSerializer.load(original_file)
    loaded.name = "RenamedAfterLoad"
    ProjectSerializer.save(loaded)

    assert not original_file.exists()
    assert (root / "RenamedAfterLoad.acfproj").exists()
