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
    UNASSESSED = "Unassessed"
    PROTOTYPE = "Prototype"
    BETA = "Beta"
    STABLE = "Stable"
    PRODUCTION = "Production"


@dataclass
class ModuleManifest:
    """
    Structured metadata manifest describing an ACF component.

    NOTE (correction — operationally dangerous): maturity/
    test_coverage_pct/doc_coverage_pct used to default to
    MaturityLevel.PRODUCTION/100.0/100.0 - the best possible score on
    every axis - for any manifest constructed without those specific
    fields explicitly measured and supplied. Combined with
    ModuleRegistryManager.scan_workspace()'s fallback (see its own
    NOTE), this meant the "maturity summary matrix" fed to the ESOC
    display could silently claim perfect production-ready, fully-
    tested, fully-documented status for modules nobody had actually
    assessed at all.
    """

    name: str
    owner: str = "Chief Systems Architect"
    version: str = "1.0.0"
    description: str = "ACF Earth System Subsystem"
    maturity: MaturityLevel = MaturityLevel.UNASSESSED
    dependencies: list[str] = field(default_factory=list)
    supported_models: list[str] = field(default_factory=lambda: ["ARPEGE", "AROME", "ALADIN", "WRF", "ICON", "IFS"])
    test_coverage_pct: float | None = None
    doc_coverage_pct: float | None = None
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
        """
        Instantiates manifest from dictionary.

        NOTE (correction): a missing or unrecognized "maturity" value
        used to silently resolve to MaturityLevel.PRODUCTION - the best
        possible score - rather than honestly signaling "not assessed".
        """
        maturity_raw = data.get("maturity", MaturityLevel.UNASSESSED.value)
        try:
            maturity_enum = MaturityLevel(maturity_raw)
        except ValueError:
            maturity_enum = MaturityLevel.UNASSESSED

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
        """
        Scans directory tree for module.yaml manifest files.

        NOTE (correction — operationally dangerous): when no
        module.yaml files exist anywhere under root_dir (which is
        genuinely the case throughout this repository - verified zero
        module.yaml files exist), this used to silently fabricate 5
        specific named manifests (hpc_connector, nwp_models,
        epygram_reader, esoc_gui, data_assimilation), each claiming
        MaturityLevel.PRODUCTION/STABLE with the dataclass's own
        fabricated 100%/100% test/doc coverage defaults (see
        ModuleManifest's own NOTE) - get_summary_matrix()'s own
        docstring says this feeds "the ESOC display", so an operator
        would see 5 modules reported as production-ready and fully
        tested/documented with zero real manifest ever read from disk.
        Fixed to honestly leave self.manifests empty when nothing is
        found, rather than inventing plausible-looking entries.
        """
        self.manifests.clear()
        manifest_files = list(self.root_dir.glob("**/module.yaml"))

        for mf in manifest_files:
            try:
                manifest = ModuleManifest.from_yaml(mf)
                self.manifests[manifest.name] = manifest
            except Exception:
                pass

        return self.manifests

    def get_summary_matrix(self) -> list[dict[str, Any]]:
        """Returns maturity summary matrix for ESOC display."""
        return [m.to_dict() for m in self.manifests.values()]
