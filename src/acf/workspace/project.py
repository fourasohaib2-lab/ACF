"""
ACF Workspace - Project

Représente un projet Atmospheric Complexity Framework.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class Project:
    """Représentation d'un projet ACF."""

    name: str
    author: str = ""
    version: str = "0.1.0"
    description: str = ""

    root_path: Path | None = None

    created: str = field(
        default_factory=lambda: datetime.now().isoformat()
    )

    modified: str = field(
        default_factory=lambda: datetime.now().isoformat()
    )

    datasets: list = field(default_factory=list)
    maps: list = field(default_factory=list)
    reports: list = field(default_factory=list)
    plugins: list = field(default_factory=list)

    settings: dict = field(
        default_factory=lambda: {
            "theme": "dark",
            "language": "fr",
        }
    )

    def update_modified(self):
        """Met à jour la date de modification."""
        self.modified = datetime.now().isoformat()

    def to_dict(self):
        """Convertit le projet en dictionnaire."""

        return {
            "name": self.name,
            "author": self.author,
            "version": self.version,
            "description": self.description,
            "root_path": str(self.root_path) if self.root_path else None,
            "created": self.created,
            "modified": self.modified,
            "datasets": self.datasets,
            "maps": self.maps,
            "reports": self.reports,
            "plugins": self.plugins,
            "settings": self.settings,
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Construit un projet à partir d'un dictionnaire."""

        root = data.get("root_path")

        return cls(
            name=data["name"],
            author=data.get("author", ""),
            version=data.get("version", "0.1.0"),
            description=data.get("description", ""),
            root_path=Path(root) if root else None,
            created=data.get("created", datetime.now().isoformat()),
            modified=data.get("modified", datetime.now().isoformat()),
            datasets=data.get("datasets", []),
            maps=data.get("maps", []),
            reports=data.get("reports", []),
            plugins=data.get("plugins", []),
            settings=data.get(
                "settings",
                {
                    "theme": "dark",
                    "language": "fr",
                },
            ),
        )
