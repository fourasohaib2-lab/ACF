"""
ACF Recent Projects Manager

Gestion des projets récemment ouverts.
"""

import json
from pathlib import Path


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

        if not self.filename.exists():
            self.projects = []

            return

        try:
            with open(self.filename, "r", encoding="utf-8") as file:
                data = json.load(file)

            self.projects = data.get("recent_projects", [])

        except Exception:
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
