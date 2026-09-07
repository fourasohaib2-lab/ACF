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

        NOTE (correction, 2026-09-07 - real bug, found while auditing
        the same real project-persistence path the RESTOR real-data
        testing led back to): Project.project_file is computed from
        the project's CURRENT name (root_path/f"{name}.acfproj") - a
        real, reachable flow (ProjectPropertiesDialog.update_project()
        changing project.name, then MenuManager.show_project_properties()
        calling save_project() right after) renames the project, but
        save() always wrote to whatever the new project_file happened
        to be, never touching the old one - confirmed by a direct test:
        renaming "OriginalName" to "RenamedName" and saving left BOTH
        OriginalName.acfproj (stale, orphaned, still holding the old
        data) and RenamedName.acfproj on disk in the same folder. Fixed
        by removing the previously-known file when the computed path
        has changed since the last real save/load of this exact Project
        instance - a genuine rename, not a guess (both paths are real,
        one is the file this object itself was last written to).
        """

        project.touch()

        data = project.to_dict()

        filename = project.project_file

        if (
            project._last_saved_path is not None
            and project._last_saved_path != filename
            and project._last_saved_path.exists()
        ):
            project._last_saved_path.unlink()

        with open(filename, "w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False,
            )

        project._last_saved_path = filename

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

        project = Project.from_dict(data)
        project._last_saved_path = filename
        return project
