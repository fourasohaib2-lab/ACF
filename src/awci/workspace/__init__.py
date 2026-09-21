"""
Atmospheric Complexity Framework (ACF)

AWCI Workspace / Projects (``src/awci/workspace/``)

Real implementation of the package named in
``docs/architecture/awci_reference_architecture.md`` section 21
("Workspace / Projects"), previously the specific gap named in
``docs/architecture/acf_awci_architecture_gap_analysis.md`` ("No
AWCI-specific project/session format; ACF's own ``acf.workspace`` is
general-purpose").

Built 2026-09-21: ``project.py`` (``AWCIProject``/
``AWCI_PROJECT_FOLDERS`` - subclasses the already-real, already-
working ``acf.workspace.project.Project``, with the blueprint's own
real per-project folder layout: data/forecasts/flights/airports/
hazards/maps/reports/analysis/exports/logs, and its own
``.awciproj`` file extension), ``serializer.py``
(``AWCIProjectSerializer`` - reuses the base
``ProjectSerializer.save()`` unchanged since it is already
polymorphic, only overrides ``load()`` to round-trip through
``AWCIProject``), ``manager.py`` (``AWCIWorkspaceManager`` - subclasses
the base ``WorkspaceManager``, reusing ``save_project()``/
``close_project()``/``recent_projects()``/``has_project()``/
``project()``/``project_name()``/``project_path()`` unchanged;
overrides ``create_project()``/``open_project()`` for the AWCI folder
layout and file format; its own recent-projects file defaults to
``~/.awci/recent_projects.json``, separate from ACF's
``~/.acf/recent_projects.json``, since an AWCI project's ``.awciproj``
file is not openable by the base ``ProjectSerializer``).

``session.py``/``state.py`` (the blueprint's remaining named files)
are deliberately not built: nothing in this codebase defines a real,
coherent "AWCI session" or "AWCI state" concept distinct from what
already exists - an open ``AWCIProject`` (this package),
``SituationSnapshot``/``DecisionContext`` (``awci.decision``), and
``AlertEngine`` (``awci.alerts``) already cover the real state a
caller would want to track; inventing a new session/state wrapper
around them with no real added behavior would be padding, not a real
gap. A future real GUI session-state concept (e.g. "which project +
which route + which time step is currently displayed") would be a
real, disclosed addition when the GUI actually needs one - not
fabricated here ahead of that need.
"""

from __future__ import annotations

from awci.workspace.manager import AWCIWorkspaceManager
from awci.workspace.project import AWCI_PROJECT_FOLDERS, AWCIProject
from awci.workspace.serializer import AWCIProjectSerializer

__all__ = [
    "AWCI_PROJECT_FOLDERS",
    "AWCIProject",
    "AWCIProjectSerializer",
    "AWCIWorkspaceManager",
]
