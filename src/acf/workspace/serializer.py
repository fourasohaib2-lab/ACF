"""
ACF Project Serializer
"""

import json
from pathlib import Path

from acf.workspace.project import Project


class ProjectSerializer:
    """
    Sauvegarde et charge les projets ACF.
    """

    @staticmethod
    def save(project: Project):
        """
        Sauvegarde un projet ACF.
        """

        project.touch()

        data = project.to_dict()

        filename = project.project_file

        with open(filename, "w", encoding="utf-8") as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False,
            )

        return filename

    ###########################################################

    @staticmethod
    def load(filename):
        """
        Charge un projet ACF.
        """

        filename = Path(filename)

        with open(filename, "r", encoding="utf-8") as file:

            data = json.load(file)

        return Project.from_dict(data)
