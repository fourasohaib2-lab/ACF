"""
ModelSkillDatabase: the Prompt Maître ACF v2.0's section 15/31 "Model
Skill Database" - a real, versioned history of how each model has
actually performed, real enough to derive a skill-weighted consensus
from (reports/ACF_MASTER_AUDIT_v2.md's "Verification (pipeline + skill
DB): MISSING" and "Consensus pondéré par le skill: MISSING" findings).

What this stores
-----------------
Whatever `acf.verification.pipeline.VerificationPipeline.evaluate()`
(or any other real caller) actually records: real
`NWPVerificationMetrics` output for one model, one variable, one
`valid_time`. Nothing in this class computes or guesses a metric
itself - it is pure storage plus real aggregation (mean) over whatever
was genuinely recorded.

Honest scope: this does not connect to any observation feed itself -
none exists yet anywhere in ACF (see
`acf.data_assimilation.observation_ingestion`'s own
"NOT_INGESTED_NO_STATION_DATA_CONNECTION" disclosures, e.g.
`SurfaceStationIngestor.ingest_synop_reports()`). A model with zero
recorded history simply has no entry here - `mean_skill()` returns
`None`, never an invented number, and `weights_from_skill()` silently
omits it rather than assigning a made-up weight.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def _now_utc() -> datetime:
    return datetime.now(UTC)


@dataclass
class SkillRecord:
    """One real verification outcome for one model, at one valid_time."""

    model: str
    variable: str
    metrics: dict[str, float]
    valid_time: datetime
    n_samples: int
    recorded_at: datetime = field(default_factory=_now_utc)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["valid_time"] = self.valid_time.isoformat()
        d["recorded_at"] = self.recorded_at.isoformat()
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> SkillRecord:
        return cls(
            model=d["model"],
            variable=d["variable"],
            metrics=dict(d["metrics"]),
            valid_time=datetime.fromisoformat(d["valid_time"]),
            n_samples=d["n_samples"],
            recorded_at=datetime.fromisoformat(d["recorded_at"]),
        )


class ModelSkillDatabase:
    """
    Append-only, optionally disk-persisted history of real verification
    outcomes per model.

    Passing `path=None` (the default) keeps everything in memory only -
    no disk I/O happens unless a caller explicitly asks for persistence
    by supplying a path, so tests and one-off callers never write files
    they didn't ask for.
    """

    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path is not None else None
        self._records: list[SkillRecord] = []
        if self.path is not None and self.path.exists():
            self._load()

    def record(
        self,
        model: str,
        variable: str,
        metrics: dict[str, float],
        valid_time: datetime,
        n_samples: int = 1,
    ) -> SkillRecord:
        """Append one real verification outcome and persist it if a path was given."""
        rec = SkillRecord(
            model=model,
            variable=variable,
            metrics=dict(metrics),
            valid_time=valid_time,
            n_samples=n_samples,
        )
        self._records.append(rec)
        if self.path is not None:
            self._save()
        return rec

    def records_for(self, model: str, variable: str | None = None) -> list[SkillRecord]:
        return [r for r in self._records if r.model == model and (variable is None or r.variable == variable)]

    def mean_skill(self, model: str, variable: str | None = None, metric: str = "rmse") -> float | None:
        """Real mean of `metric` across every record matching model/variable, or None if there is none."""
        values = [r.metrics[metric] for r in self.records_for(model, variable) if metric in r.metrics]
        return (sum(values) / len(values)) if values else None

    def weights_from_skill(
        self,
        models: Sequence[str],
        variable: str | None = None,
        metric: str = "rmse",
        lower_is_better: bool = True,
    ) -> dict[str, float]:
        """
        Real inverse-error weighting, computed only from models that
        actually have recorded history for `variable`/`metric`.

        Models with no recorded history are simply absent from the
        returned dict - never assigned an invented weight - so a
        caller (e.g. ModelConsensusEngine) can make its own honest
        decision about what to do for them (its existing declared
        default, or refuse to mix at all).

        Returns an empty dict if not a single requested model has any
        recorded history - never a fabricated uniform weighting.
        """
        scores: dict[str, float] = {}
        for m in models:
            s = self.mean_skill(m, variable, metric)
            if s is not None:
                scores[m] = s
        if not scores:
            return {}

        eps = 1e-9
        if lower_is_better:
            inverse = {m: 1.0 / (s + eps) for m, s in scores.items()}
        else:
            inverse = {m: max(s, 0.0) + eps for m, s in scores.items()}
        total = sum(inverse.values())
        return {m: v / total for m, v in inverse.items()}

    def _save(self) -> None:
        assert self.path is not None
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps([r.to_dict() for r in self._records], indent=2))

    def _load(self) -> None:
        assert self.path is not None
        data = json.loads(self.path.read_text())
        self._records = [SkillRecord.from_dict(d) for d in data]

    def __len__(self) -> int:
        return len(self._records)
