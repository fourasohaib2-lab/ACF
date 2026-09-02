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

    def __init__(self, recent_projects_file=None):
        """
        NOTE (correction — real state leak, confirmed on disk): with no way
        to override RecentProjectsManager's file, every WorkspaceManager()
        - including every test that calls create_project()/save_project()/
        open_project() - wrote to the real ~/.acf/recent_projects.json on
        whatever machine ran it, regardless of test isolation elsewhere
        (create_project's own project files were correctly written under
        pytest's tmp_path, but the "recent project" entry itself leaked
        into the real user's persistent config either way). Confirmed:
        this machine's actual ~/.acf/recent_projects.json contained
        multiple /tmp/pytest-of-.../test_.../Demo/Demo.acfproj entries
        from past test runs. recent_projects_file lets a caller (tests,
        primarily) inject an isolated path instead; defaults to the same
        real location as before for actual application use.
        """

        self.current_project = None

        self.recent = RecentProjectsManager(recent_projects_file)

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
