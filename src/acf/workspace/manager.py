"""
ACF Workspace Manager
"""

from pathlib import Path

from acf.workspace.project import Project
from acf.workspace.recent import RecentProjectsManager
from acf.workspace.serializer import ProjectSerializer


class WorkspaceManager:
    """
    Gestionnaire des projets ACF.
    """

    def __init__(self):

        self.current_project = None

        self.recent = RecentProjectsManager()

    # ======================================================
    # Création
    # ======================================================

    def create_project(
        self,
        name: str,
        directory,
        author: str = "",
        description: str = "",
    ) -> Project:

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
            root_path=root,
            author=author,
            description=description,
        )

        ProjectSerializer.save(project)

        self.current_project = project

        # Ajouter aux projets récents

        self.recent.add(project.project_file)

        return project

    # ======================================================
    # Ouverture
    # ======================================================

    def open_project(self, filename) -> Project:

        project = ProjectSerializer.load(filename)

        self.current_project = project

        # Ajouter aux projets récents

        self.recent.add(filename)

        return project

    # ======================================================
    # Sauvegarde
    # ======================================================

    def save_project(self):

        if self.current_project is None:
            raise RuntimeError("No project opened.")

        ProjectSerializer.save(self.current_project)

    # ======================================================
    # Fermeture
    # ======================================================

    def close_project(self):

        self.current_project = None

    # ======================================================
    # Projets récents
    # ======================================================

    def recent_projects(self):

        return self.recent.get_projects()

    # ======================================================
    # Informations
    # ======================================================

    def has_project(self) -> bool:

        return self.current_project is not None

    def project(self):

        return self.current_project

    def project_name(self):

        if self.current_project is None:
            return None

        return self.current_project.name

    def project_path(self):

        if self.current_project is None:
            return None

        return self.current_project.root_path
