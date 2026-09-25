"""
Atmospheric Complexity Framework (ACF)

AWCI Workspace - Manager

Real ``AWCIWorkspaceManager`` - the ``manager.py`` module named in
``docs/architecture/awci_reference_architecture.md`` section 21.
Subclasses the already-real, already-working
``acf.workspace.manager.WorkspaceManager`` - ``save_project()``,
``close_project()``, ``recent_projects()``, ``has_project()``,
``project()``, ``project_name()``, ``project_path()`` are all reused
unchanged (inherited): they already operate generically on
``self.current_project``/``self.recent`` with no ``Project``-specific
construction inside them. Only ``create_project()`` and
``open_project()`` are overridden, since the base class hardcodes the
ACF folder layout and the base ``Project``/``ProjectSerializer``
classes rather than the AWCI ones.
"""

from __future__ import annotations

from pathlib import Path

from acf.workspace.manager import WorkspaceManager

from awci.workspace.project import AWCI_PROJECT_FOLDERS, AWCIProject
from awci.workspace.serializer import AWCIProjectSerializer


class AWCIWorkspaceManager(WorkspaceManager):
    """Real AWCI project lifecycle manager - same real
    create/open/save/close/recent-projects behavior as
    ``acf.workspace.manager.WorkspaceManager``, specialized to
    ``AWCIProject``'s own real ``.awciproj`` file format and
    ``AWCI_PROJECT_FOLDERS`` folder layout."""

    def __init__(self, recent_projects_file=None) -> None:
        """Real override of the base constructor's default recent-
        projects path: an AWCI project's "recent" entry must not mix
        with ACF's own ``~/.acf/recent_projects.json`` (different
        project file format, ``.awciproj`` vs ``.acfproj`` - listing an
        AWCI project there would let a caller try to open it with the
        wrong serializer). Defaults to ``~/.awci/recent_projects.json``;
        ``recent_projects_file`` still lets a caller override it (tests,
        primarily), same as the base class."""
        if recent_projects_file is None:
            recent_projects_file = Path.home() / ".awci" / "recent_projects.json"
        super().__init__(recent_projects_file=recent_projects_file)

    def create_project(
        self,
        name: str,
        directory,
        author: str = "",
        description: str = "",
    ) -> AWCIProject:
        """Real AWCI project creation - identical real directory-
        creation/serialization/recent-tracking flow as the base
        ``create_project()``, using ``AWCI_PROJECT_FOLDERS`` (data/
        forecasts/flights/airports/hazards/maps/reports/analysis/
        exports/logs) instead of ACF's own general-purpose folder set,
        and constructing an ``AWCIProject`` instead of the base
        ``Project``."""
        root = Path(directory) / name
        root.mkdir(parents=True, exist_ok=True)

        for folder in AWCI_PROJECT_FOLDERS:
            (root / folder).mkdir(exist_ok=True)

        project = AWCIProject(
            name=name,
            root_path=root,
            author=author,
            description=description,
        )

        AWCIProjectSerializer.save(project)

        self.current_project = project
        self.recent.add(project.project_file)

        return project

    def open_project(self, filename) -> AWCIProject:
        """Real AWCI project open - identical real flow to the base
        ``open_project()``, loading through ``AWCIProjectSerializer``
        so the result is a real ``AWCIProject``."""
        project = AWCIProjectSerializer.load(filename)

        self.current_project = project
        self.recent.add(filename)

        return project
