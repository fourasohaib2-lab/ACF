"""
Workspace Serializer
"""

import json
from pathlib import Path

from acf.workspace.project import Project


class ProjectSerializer:

    FILE_EXTENSION = ".acfproj"

    @classmethod
    def save(cls, project: Project):

        if project.root_path is None:
            raise ValueError("Project has no root path.")

        file = project.root_path / f"{project.name}{cls.FILE_EXTENSION}"

        with open(file, "w", encoding="utf-8") as f:
            json.dump(
                project.to_dict(),
                f,
                indent=4,
                ensure_ascii=False,
            )

    @classmethod
    def load(cls, filename):

        filename = Path(filename)

        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)

        return Project.from_dict(data)
