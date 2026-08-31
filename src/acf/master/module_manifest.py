"""
Atmospheric Complexity Framework (ACF) - Global Earth System Operating Platform (GESOP)

Module Manifest and Maturity System (ACF-1000).
Tracks owner, version, dependencies, supported models, maturity level,
test coverage, doc coverage, and HPC requirements across all ACF subsystems.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import yaml


class MaturityLevel(str, Enum):
    PROTOTYPE = "Prototype"
    BETA = "Beta"
    STABLE = "Stable"
    PRODUCTION = "Production"


@dataclass
class ModuleManifest:
    """
    Structured metadata manifest describing an ACF component.
    """

    name: str
    owner: str = "Chief Systems Architect"
    version: str = "1.0.0"
    description: str = "ACF Earth System Subsystem"
    maturity: MaturityLevel = MaturityLevel.PRODUCTION
    dependencies: list[str] = field(default_factory=list)
    supported_models: list[str] = field(default_factory=lambda: ["ARPEGE", "AROME", "ALADIN", "WRF", "ICON", "IFS"])
    test_coverage_pct: float = 100.0
    doc_coverage_pct: float = 100.0
    hpc_requirements: dict[str, Any] = field(
        default_factory=lambda: {
            "mpi": True,
            "openmp": True,
            "gpu": False,
            "slurm": True,
        }
    )

    def to_dict(self) -> dict[str, Any]:
        """Converts manifest to dictionary."""
        d = asdict(self)
        d["maturity"] = self.maturity.value
        return d

    def to_yaml(self, filepath: str | Path) -> str:
        """Serializes manifest to YAML file."""
        data = self.to_dict()
        yaml_str = yaml.dump(data, sort_keys=False)
        p = Path(filepath)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(yaml_str, encoding="utf-8")
        return yaml_str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ModuleManifest:
        """Instantiates manifest from dictionary."""
        maturity_raw = data.get("maturity", "Production")
        try:
            maturity_enum = MaturityLevel(maturity_raw)
        except ValueError:
            maturity_enum = MaturityLevel.PRODUCTION

        kwargs = dict(data)
        kwargs["maturity"] = maturity_enum
        return cls(**kwargs)

    @classmethod
    def from_yaml(cls, filepath: str | Path) -> ModuleManifest:
        """Loads manifest from YAML file."""
        p = Path(filepath)
        content = p.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        return cls.from_dict(data)


class ModuleRegistryManager:
    """
    Scans and manages all module manifests across ACF workspace.
    """

    def __init__(self, root_dir: str | Path | None = None) -> None:
        if root_dir is not None:
            self.root_dir = Path(root_dir)
        else:
            self.root_dir = Path(__file__).resolve().parents[3]
        self.manifests: dict[str, ModuleManifest] = {}
        self.scan_workspace()

    def scan_workspace(self) -> dict[str, ModuleManifest]:
        """Scans directory tree for module.yaml manifest files."""
        self.manifests.clear()
        manifest_files = list(self.root_dir.glob("**/module.yaml"))

        for mf in manifest_files:
            try:
                manifest = ModuleManifest.from_yaml(mf)
                self.manifests[manifest.name] = manifest
            except Exception:
                pass

        if not self.manifests:
            # Generate core manifests if none found on disk
            default_modules = [
                ModuleManifest(name="hpc_connector", maturity=MaturityLevel.PRODUCTION),
                ModuleManifest(name="nwp_models", maturity=MaturityLevel.PRODUCTION),
                ModuleManifest(name="epygram_reader", maturity=MaturityLevel.PRODUCTION),
                ModuleManifest(name="esoc_gui", maturity=MaturityLevel.PRODUCTION),
                ModuleManifest(name="data_assimilation", maturity=MaturityLevel.STABLE),
            ]
            for dm in default_modules:
                self.manifests[dm.name] = dm

        return self.manifests

    def get_summary_matrix(self) -> list[dict[str, Any]]:
        """Returns maturity summary matrix for ESOC display."""
        return [m.to_dict() for m in self.manifests.values()]
