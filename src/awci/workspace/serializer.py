"""
Atmospheric Complexity Framework (ACF)

AWCI Workspace - Serializer

Real ``AWCIProjectSerializer`` - the ``serializer.py`` module named in
``docs/architecture/awci_reference_architecture.md`` section 21.
``save()`` is the already-real, already-working
``acf.workspace.serializer.ProjectSerializer.save()`` reused directly
(unchanged) - it already operates polymorphically on whatever
``Project``-shaped object it is given (``project.to_dict()``/
``project.project_file``/``project.touch()``), so it correctly writes
an ``AWCIProject`` to its own real ``.awciproj`` path with zero
duplicated logic, including the base serializer's own real rename-
cleanup fix (removing a stale old file on a genuine project rename).
Only ``load()`` needs a real override, since the base
``ProjectSerializer.load()`` hardcodes construction of the base
``Project`` class rather than the caller's subclass.
"""

from __future__ import annotations

import json
from pathlib import Path

from acf.workspace.serializer import ProjectSerializer

from awci.workspace.project import AWCIProject


class AWCIProjectSerializer:
    """Real AWCI project persistence - same real JSON file format as
    ``acf.workspace.serializer.ProjectSerializer``, but round-trips
    through ``AWCIProject`` rather than the base ``Project`` class."""

    #: Reuses the base serializer's own real save() unchanged - it is
    #: already polymorphic over any Project-shaped instance.
    save = staticmethod(ProjectSerializer.save)

    @staticmethod
    def load(filename) -> AWCIProject:
        """Real load - identical real JSON-read logic to
        ``ProjectSerializer.load()``, building an ``AWCIProject``
        instead of the base ``Project`` so the on-disk ``.awciproj``
        extension and folder-layout constant travel with the loaded
        object."""
        filename = Path(filename)

        with open(filename, encoding="utf-8") as file:
            data = json.load(file)

        project = AWCIProject.from_dict(data)
        project._last_saved_path = filename
        return project
