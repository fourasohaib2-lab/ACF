"""
Atmospheric Complexity Framework (ACF) - Forecast Configuration Engine (ACF-NWP-001)

Provides structured configuration management for NWP model runs (domain, resolution,
nesting, forecast length, initial/boundary conditions, physics schemes, output frequency, restart interval).
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ForecastConfig:
    """
    Structured forecast configuration container.
    """

    model_name: str = "AROME"
    domain: str = "Algeria_Domain"
    resolution_km: float = 1.3
    nesting_level: int = 1
    forecast_hours: int = 48
    initial_conditions: str = "ARPEGE_ANALYSIS"
    boundary_conditions: str = "ARPEGE_COUPLING"
    physics_schemes: dict[str, str] = field(
        default_factory=lambda: {
            "microphysics": "ICE3",
            "convection": "EXPLICIT",
            "radiation": "RRTM",
            "surface": "SURFEX_ISBA",
            "turbulence": "CBR",
        }
    )
    output_frequency_hours: int = 1
    restart_interval_hours: int = 6
    hpc_nodes: int = 4
    hpc_cpus_per_node: int = 32

    def validate(self) -> bool:
        """Validates parameters for numerical stability."""
        if self.forecast_hours <= 0:
            raise ValueError("forecast_hours must be positive")
        if self.resolution_km <= 0:
            raise ValueError("resolution_km must be positive")
        if self.output_frequency_hours <= 0:
            raise ValueError("output_frequency_hours must be positive")
        return True

    def to_dict(self) -> dict[str, Any]:
        """Converts configuration to dictionary."""
        self.validate()
        return asdict(self)

    def to_json(self, filepath: str | None = None) -> str:
        """Serializes configuration to JSON string or file."""
        data = self.to_dict()
        json_str = json.dumps(data, indent=2)
        if filepath:
            out_p = Path(filepath)
            out_p.parent.mkdir(parents=True, exist_ok=True)
            out_p.write_text(json_str, encoding="utf-8")
        return json_str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ForecastConfig:
        """Instantiates ForecastConfig from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    @classmethod
    def from_json(cls, filepath_or_str: str) -> ForecastConfig:
        """Instantiates ForecastConfig from JSON string or file path."""
        p = Path(filepath_or_str)
        if p.exists() and p.is_file():
            content = p.read_text(encoding="utf-8")
        else:
            content = filepath_or_str
        return cls.from_dict(json.loads(content))
