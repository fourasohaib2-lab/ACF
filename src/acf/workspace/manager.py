"""
Workspace Manager
"""

from pathlib import Path

from acf.workspace.project import Project
from acf.workspace.serializer import ProjectSerializer


class WorkspaceManager:

    def __init__(self):

        self.current_project = None

    ########################################################

    def create_project(
        self,
        name,
        directory,
        author="",
        description=""
    ):

        root = Path(directory) / name

        root.mkdir(parents=True, exist_ok=True)

        folders = [
            "data",
            "maps",
            "models",
            "reports",
            "scripts",
            "exports",
            "logs",
            "cache",
            "plugins",
        ]

        for folder in folders:
            (root / folder).mkdir(exist_ok=True)

        project = Project(
            name=name,
            author=author,
            description=description,
            root_path=root,
        )

        ProjectSerializer.save(project)

        self.current_project = project

        return project

    ########################################################

    def open_project(self, filename):

        project = ProjectSerializer.load(filename)

        self.current_project = project

        return project

    ########################################################

    def save_project(self):

        if self.current_project is None:
            raise RuntimeError("No project opened.")

        ProjectSerializer.save(self.current_project)

    ########################################################

    def close_project(self):

        self.current_project = None
