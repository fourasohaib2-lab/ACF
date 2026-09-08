"""
AWCI External Versioned Configuration (§56)
================================================

docs/ACF_MASTER_PROMPT.md section 56:

    "Les seuils et poids ne doivent pas être codés en dur partout.
    Prévoir une configuration versionnée (modules, normalisation AWCI,
    poids, seuils)."

Found during this session's exhaustive 90-section conformance audit
(reports/ACF_MASTER_AUDIT_v2.md): `WeightsManager.DEFAULT_WEIGHTS`/
`AWCICalculator.INTERACTION_TERMS`/`INTERACTION_WEIGHTS`/
`LEVEL_THRESHOLDS` are already real, per-instance CONFIGURABLE
(`AWCICalculator.__init__()`'s own `weights`/`interaction_terms`/
`interaction_weights`/`level_thresholds` parameters, built at sections
22/45-47 of this same session) - but their real VALUES still only ever
came from Python source constants, never an external, versioned config
FILE a real operator could edit/version without touching code.

Honest scope
-------------
`load_config()` reuses AWCICalculator's own already-real constructor
(never reimplements its validation - key-matching interaction
terms/weights, strictly-ascending level thresholds) to validate a
loaded config is genuinely usable, the same real discipline
acf.awci.calibration.lock_calibration() already established. JSON, not
YAML - this project's own already-established real persistence format
(acf.testing.golden, acf.awci.validation_cases both already use it) -
not a new, previously-undeclared dependency (PyYAML is not a real
declared dependency of this project - see this session's own earlier
"audit complet des dépendances non déclarées" finding for why that
distinction matters here).

`config_version` reuses the exact same field name as
`acf.core.contracts.provenance.Provenance.config_version` (built at
sections 57-58 of this session) - not a separately invented
versioning convention.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from acf.awci.calculator import AWCICalculator


@dataclass(frozen=True)
class AWCIConfig:
    """Real, external, versioned AWCI configuration (docs/ACF_MASTER_PROMPT.md section 56)."""

    config_version: str
    weights: dict[str, float]
    interaction_terms: dict[str, tuple[str, ...]]
    interaction_weights: dict[str, float]
    level_thresholds: tuple[tuple[float, str], ...]

    def build_calculator(self) -> AWCICalculator:
        """Real AWCICalculator constructed from exactly this config -
        defensive copies of the mutable fields, same discipline as
        acf.awci.calibration.LockedModel.build_calculator()."""
        return AWCICalculator(
            weights=dict(self.weights),
            interaction_terms=dict(self.interaction_terms),
            interaction_weights=dict(self.interaction_weights),
            level_thresholds=self.level_thresholds,
        )


def load_config(path: Path | str) -> AWCIConfig:
    """
    Real loader: parses a real JSON file into an AWCIConfig, validating
    it by genuinely constructing an AWCICalculator from it (the same
    real validation AWCICalculator.__init__() already performs - never
    reimplemented here).

    Expected real JSON shape::

        {
          "config_version": "2026.09-v1",
          "weights": {"dynamic": 0.20, ...},
          "interaction_terms": {"wind_topo_interaction": ["dynamic", "topographic"], ...},
          "interaction_weights": {"wind_topo_interaction": 0.05, ...},
          "level_thresholds": [[20.0, "Very Low"], [35.0, "Low"], ..., [null, "Extreme"]]
        }

    A `null` bound in the last `level_thresholds` entry (JSON has no
    native `Infinity` literal usable this way in every real parser) is
    read as `float("inf")` - the real, exact value
    `AWCICalculator.LEVEL_THRESHOLDS`'s own last entry already uses.

    Raises
    ------
    ValueError
        If a required real key is missing, or if the resulting
        configuration is invalid (propagated from
        AWCICalculator.__init__()'s own real validation).
    """
    payload = json.loads(Path(path).read_text(encoding="utf-8"))

    required_keys = {"config_version", "weights", "interaction_terms", "interaction_weights", "level_thresholds"}
    missing = required_keys - payload.keys()
    if missing:
        raise ValueError(f"Config file {path} is missing required key(s): {sorted(missing)}")

    interaction_terms = {name: tuple(modules) for name, modules in payload["interaction_terms"].items()}
    level_thresholds = tuple(
        (float("inf") if bound is None else float(bound), label) for bound, label in payload["level_thresholds"]
    )

    config = AWCIConfig(
        config_version=payload["config_version"],
        weights=dict(payload["weights"]),
        interaction_terms=interaction_terms,
        interaction_weights=dict(payload["interaction_weights"]),
        level_thresholds=level_thresholds,
    )
    # Real validation - reuses AWCICalculator.__init__()'s own checks,
    # never reimplemented here (raises ValueError on a real mismatch).
    config.build_calculator()
    return config


def save_default_config(path: Path | str, config_version: str = "unknown") -> None:
    """
    Real export: writes AWCICalculator's own compiled-in real defaults
    (INTERACTION_TERMS/INTERACTION_WEIGHTS/LEVEL_THRESHOLDS,
    WeightsManager.DEFAULT_WEIGHTS) as a real, versioned starting
    config file - a real caller's own real editing starting point, not
    a fabricated example.
    """
    from acf.awci.weights import WeightsManager

    payload: dict[str, Any] = {
        "config_version": config_version,
        "weights": dict(WeightsManager.DEFAULT_WEIGHTS),
        "interaction_terms": {name: list(modules) for name, modules in AWCICalculator.INTERACTION_TERMS.items()},
        "interaction_weights": dict(AWCICalculator.INTERACTION_WEIGHTS),
        "level_thresholds": [
            [None if bound == float("inf") else bound, label] for bound, label in AWCICalculator.LEVEL_THRESHOLDS
        ],
    }
    Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
