"""
ACF Project Serializer
"""

import json
from dataclasses import asdict
from pathlib import Path

from acf.workspace.project import Project


class ProjectSerializer:
    """
    Sauvegarde et charge les projets ACF.
    """

    @staticmethod
    def save(project: Project):

        project.touch()

        data = asdict(project)

        # Conversion Path -> str
        data["root_path"] = str(project.root_path)

        filename = project.project_file

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                indent=4,
                ensure_ascii=False,
            )

    ########################################################

    @staticmethod
    def load(filename):

        filename = Path(filename)

        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)

        data["root_path"] = Path(data["root_path"])

        return Project(**data)
