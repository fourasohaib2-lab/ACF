"""
ACF Project
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class Project:
    """
    Représente un projet ACF.
    """

    # =====================================================
    # Informations générales
    # =====================================================

    name: str

    root_path: Path = Path(".")

    author: str = ""

    description: str = ""

    version: str = "0.1.0"

    created: str = field(default_factory=lambda: datetime.now().isoformat())

    modified: str = field(default_factory=lambda: datetime.now().isoformat())

    # =====================================================
    # Ressources
    # =====================================================

    datasets: list = field(default_factory=list)

    maps: list = field(default_factory=list)

    models: list = field(default_factory=list)

    reports: list = field(default_factory=list)

    scripts: list = field(default_factory=list)

    plugins: list = field(default_factory=list)

    metadata: dict = field(default_factory=dict)

    settings: dict = field(default_factory=dict)

    # =====================================================

    @property
    def project_file(self):
        """
        Fichier principal du projet.
        """
        return self.root_path / f"{self.name}.acfproj"

    @property
    def metadata_file(self):
        """
        Métadonnées.
        """
        return self.root_path / "metadata.json"

    # =====================================================

    def touch(self):
        """
        Met à jour la date de modification.
        """
        self.modified = datetime.now().isoformat()

    # =====================================================

    def summary(self):

        return {
            "name": self.name,
            "author": self.author,
            "version": self.version,
            "datasets": len(self.datasets),
            "maps": len(self.maps),
            "models": len(self.models),
            "reports": len(self.reports),
            "scripts": len(self.scripts),
            "plugins": len(self.plugins),
        }

    # =====================================================

    def to_dict(self):
        """
        NOTE (correction): used to omit datasets/maps/models/reports/
        scripts/plugins entirely, and from_dict() (see below) silently
        dropped even the fields that were here (metadata, settings,
        created) - every ProjectSerializer.save()+load() round-trip
        (the only persistence path WorkspaceManager uses) silently
        discarded a project's resource lists, metadata, settings, and
        original creation date, replacing "created" with a fresh
        "now" timestamp. Now included so save()+load() is a faithful
        round-trip.
        """
        return {
            "name": self.name,
            "author": self.author,
            "description": self.description,
            "version": self.version,
            "root_path": str(self.root_path),
            "created": self.created,
            "modified": self.modified,
            "datasets": self.datasets,
            "maps": self.maps,
            "models": self.models,
            "reports": self.reports,
            "scripts": self.scripts,
            "plugins": self.plugins,
            "metadata": self.metadata,
            "settings": self.settings,
        }

    # =====================================================

    @classmethod
    def from_dict(cls, data):

        project = cls(
            name=data.get("name", ""),
            root_path=Path(data.get("root_path", ".")),
            author=data.get("author", ""),
            description=data.get("description", ""),
            version=data.get("version", "0.1.0"),
        )

        if "created" in data:
            project.created = data["created"]
        if "modified" in data:
            project.modified = data["modified"]
        project.datasets = data.get("datasets", [])
        project.maps = data.get("maps", [])
        project.models = data.get("models", [])
        project.reports = data.get("reports", [])
        project.scripts = data.get("scripts", [])
        project.plugins = data.get("plugins", [])
        project.metadata = data.get("metadata", {})
        project.settings = data.get("settings", {})

        return project

    # =====================================================

    def __repr__(self):

        return f"Project(name='{self.name}', version='{self.version}')"
