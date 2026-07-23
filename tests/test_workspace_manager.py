from pathlib import Path

from acf.workspace.manager import WorkspaceManager


def test_create_project(tmp_path):

    manager = WorkspaceManager()

    project = manager.create_project(
        name="Demo",
        directory=tmp_path,
    )

    assert project.name == "Demo"

    assert (tmp_path / "Demo").exists()

    assert (tmp_path / "Demo" / "data").exists()

    assert (tmp_path / "Demo" / "Demo.acfproj").exists()
