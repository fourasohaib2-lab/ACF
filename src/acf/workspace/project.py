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
    root_path: Path

    author: str = ""
    description: str = ""

    version: str = "0.1.0-alpha"

    created: str = field(
        default_factory=lambda: datetime.now().isoformat()
    )

    modified: str = field(
        default_factory=lambda: datetime.now().isoformat()
    )

    # =====================================================
    # Ressources du projet
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
        return self.root_path / "project.acf"

    @property
    def metadata_file(self):
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
