"""
ACF Recent Projects Manager

Gestion des projets récemment ouverts.
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class RecentProjectsManager:
    """
    Gestionnaire des projets récents ACF.
    """

    MAX_PROJECTS = 10

    def __init__(self, filename=None):

        if filename is None:
            filename = Path.home() / ".acf" / "recent_projects.json"

        self.filename = Path(filename)

        self.filename.parent.mkdir(parents=True, exist_ok=True)

        self.projects = []

        self.load()

    ##################################################

    def load(self):
        """
        NOTE (correction, 2026-09-05 - post-model4d audit): this bare
        `except Exception: pass` used to silently swallow ANY error
        reading/parsing self.filename - a genuinely present but
        corrupted recent_projects.json (truncated write, disk full,
        manual edit) was treated identically to "no file yet", silently
        discarding the user's real recent-projects list with no log at
        all. The next add()/remove()/get_projects() call would then
        overwrite the corrupted file with an empty one - real, silent
        data loss. Same bug class already found and fixed twice
        elsewhere in this codebase (hpc_workflow/workflow_configuration.py's
        config loader, master/module_manifest.py's scan_workspace() -
        this file predates neither pass, so was never covered by
        either). Now logs a real warning instead of silently
        discarding.
        """
        if not self.filename.exists():
            self.projects = []

            return

        try:
            with open(self.filename, "r", encoding="utf-8") as file:
                data = json.load(file)

            self.projects = data.get("recent_projects", [])

        except Exception:
            logger.warning(
                "Failed to load recent projects from %s - starting from an empty list instead",
                self.filename,
                exc_info=True,
            )
            self.projects = []

    ##################################################

    def save(self):

        data = {"recent_projects": self.projects}

        with open(self.filename, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    ##################################################

    def add(self, project_file):

        project_file = str(Path(project_file))

        if project_file in self.projects:
            self.projects.remove(project_file)

        self.projects.insert(0, project_file)

        self.projects = self.projects[: self.MAX_PROJECTS]

        self.save()

    ##################################################

    def remove(self, project_file):

        project_file = str(Path(project_file))

        if project_file in self.projects:
            self.projects.remove(project_file)

            self.save()

    ##################################################

    def get_projects(self):

        valid = []

        for project in self.projects:
            if Path(project).exists():
                valid.append(project)

        self.projects = valid

        self.save()

        return self.projects

    ##################################################

    def clear(self):

        self.projects = []

        self.save()
