"""
Atmospheric Complexity Framework (ACF)

AWCI Workspace - Project

Real ``AWCIProject`` - the ``project.py`` module named in
``docs/architecture/awci_reference_architecture.md`` section 21
("Workspace / Projects"). Subclasses the already-real, already-working
``acf.workspace.project.Project`` dataclass (name/author/description/
version/created/modified/metadata/settings, real JSON round-trip via
``to_dict()``/``from_dict()``) rather than a second, independently
invented project dataclass - only the on-disk file extension and the
real per-project folder layout differ.

The blueprint's own text for this section: "An AWCI project keeps:
``data/ forecasts/ flights/ airports/ hazards/ maps/ reports/
analysis/ exports/ logs/``" - a different real folder set from ACF's
own general-purpose project (``data/maps/models/reports/scripts/
exports/logs/cache/plugins``, see ``acf.workspace.manager.
WorkspaceManager.create_project()``), reflecting AWCI's own real
aviation-weather-intelligence scope (flights/airports/hazards, not
models/scripts/plugins).
"""

from __future__ import annotations

from pathlib import Path

from acf.workspace.project import Project

#: Real per-project folder layout for an AWCI project - exactly the
#: set named in ``docs/architecture/awci_reference_architecture.md``
#: section 21, not ACF's own general-purpose folder set.
AWCI_PROJECT_FOLDERS: tuple[str, ...] = (
    "data",
    "forecasts",
    "flights",
    "airports",
    "hazards",
    "maps",
    "reports",
    "analysis",
    "exports",
    "logs",
)


class AWCIProject(Project):
    """
    Real AWCI-specific project - identical real fields and JSON
    round-trip behavior to ``acf.workspace.project.Project`` (inherited
    unchanged), except its on-disk file uses the ``.awciproj``
    extension rather than ``.acfproj`` so an AWCI project and an ACF
    project never collide in the same directory.
    """

    @property
    def project_file(self) -> Path:
        """Real AWCI project file - same real
        ``root_path / f"{name}.<ext>"`` convention as the base
        ``Project``, with the AWCI-specific ``.awciproj`` extension."""
        return self.root_path / f"{self.name}.awciproj"

    @classmethod
    def from_dict(cls, data: dict) -> AWCIProject:
        """Real round-trip construction - reuses the base
        ``Project.from_dict()`` field-population logic entirely
        (never duplicated), only building the AWCI subclass instead of
        the base class."""
        base = Project.from_dict(data)
        project = cls(
            name=base.name,
            root_path=base.root_path,
            author=base.author,
            description=base.description,
            version=base.version,
        )
        project.created = base.created
        project.modified = base.modified
        project.datasets = base.datasets
        project.maps = base.maps
        project.models = base.models
        project.reports = base.reports
        project.scripts = base.scripts
        project.plugins = base.plugins
        project.metadata = base.metadata
        project.settings = base.settings
        return project

    def __repr__(self) -> str:
        return f"AWCIProject(name='{self.name}', version='{self.version}')"
