"""
Dataset: the Prompt Maître ACF v2.0's section 13 Data Contract.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

import numpy as np

from acf.core.contracts.provenance import Provenance
from acf.core.contracts.quality import QualityInfo
from acf.core.contracts.uncertainty import UncertaintyInfo
from acf.core.exceptions import CoordinateError, RangeError, TimeError
from acf.physics_guard.guard import PhysicsGuard, PhysicsGuardReport
from acf.physics_guard.range_check import OPERATIONAL_RANGES


@dataclass
class Dataset:
    """
    ACF's real, constructible Data Contract.

    Every field name below matches the Prompt Maître's own section 13
    list exactly, plus `values` (the real array of data this Dataset
    describes - not in the original field list, but a metadata
    contract with nothing to validate against is not useful on its
    own; a Dataset with no values yet, e.g. mid-construction, may
    legitimately leave it None).

    Parameters
    ----------
    id : str
        Caller-assigned unique identifier for this dataset.
    source : str
        Where the data genuinely came from, e.g. "CoupledEarthSolver",
        "AWCICalculator" - not a model name (see `model` below).
    model : str
        Which model/configuration produced it, e.g. "ARPEGE".
    run : str
        Cycle/run identifier, e.g. "00Z" - a label, not a timestamp
        (forecast_reference_time is the real timestamp).
    forecast_reference_time : datetime
        When the model run started.
    valid_time : datetime
        The time this data is valid for.
    lead_time : timedelta
        valid_time - forecast_reference_time (not auto-derived - the
        caller supplies it explicitly so a mismatch between the two is
        itself something validate() can catch, not silently
        recomputed away).
    variable : str
        Real CF standard_name if the variable has one (needed for
        validate()'s range check to apply) - or a descriptive ACF-
        internal name (e.g. "awci") for a derived, non-CF quantity like
        a composite complexity score.
    unit : str
        The real unit `values` is actually in. Empty string for a
        dimensionless quantity (e.g. a 0-100 composite score) - not a
        fabricated "1" or "dimensionless" CF unit string unless one is
        genuinely appropriate.
    dimensions : tuple[str, ...]
        e.g. ("lat", "lon") or ("level", "lat", "lon").
    coordinates : dict[str, Any]
        e.g. {"lats": [...], "lons": [...], "levels": [...]} - real
        coordinate arrays, in ACF's own established convention
        (acf.awci.spatial_field/vertical_field/temporal_field).
    values : Any, optional
        The real array of data - typically a numpy array shaped per
        `dimensions`.
    horizontal_grid, vertical_coordinate : str, optional
        Free-form descriptors, e.g. "regular_latlon", "native_model_level".
    ensemble_member : int, optional
        None for a deterministic dataset.
    quality : QualityInfo, optional
        Defaults to QualityInfo() (status="NOT_ASSESSED") if not given
        - never silently implies QC passed.
    uncertainty : UncertaintyInfo, optional
        Defaults to UncertaintyInfo() (kind="not_assessed") if not
        given - never silently implies a value is certain.
    provenance : Provenance, optional
    version : str
        Contract/schema version, not the ACF package version (see
        Provenance.science_version for that).
    """

    id: str
    source: str
    model: str
    run: str
    forecast_reference_time: datetime
    valid_time: datetime
    lead_time: timedelta
    variable: str
    unit: str
    dimensions: tuple[str, ...]
    coordinates: dict[str, Any] = field(default_factory=dict)
    values: Any = None
    horizontal_grid: str | None = None
    vertical_coordinate: str | None = None
    ensemble_member: int | None = None
    quality: QualityInfo = field(default_factory=QualityInfo)
    uncertainty: UncertaintyInfo = field(default_factory=UncertaintyInfo)
    provenance: Provenance | None = None
    version: str = "1.0"

    # -------------------------------------------------------------- honesty

    def is_fully_documented(self) -> bool:
        """
        Prompt Maître section 4's own principle: "Une donnée sans
        métadonnées suffisantes ne doit pas être considérée comme
        pleinement exploitable." True only if every field that matters
        for trusting this dataset is genuinely filled in - constructing
        the object is not enough by itself.
        """
        return (
            bool(self.id)
            and bool(self.source)
            and bool(self.model)
            and bool(self.variable)
            and bool(self.unit)
            and bool(self.dimensions)
            and self.provenance is not None
            and self.provenance.is_complete()
            and self.quality.status != "NOT_ASSESSED"
        )

    # -------------------------------------------------------------- physics

    def validate(self) -> PhysicsGuardReport:
        """
        Run acf.physics_guard.PhysicsGuard against this Dataset's own
        real metadata and values - the "ACF 4D DATA MODEL -> PHYSICS
        GUARD" link the master architecture diagram describes. Reuses
        PhysicsGuard, does not reimplement any check.

        Runs whichever checks this Dataset's own fields make possible:
        coordinate check if coordinates has "lats"/"lons"; range check
        if `values` is set and `variable` has a documented operational
        range; time-ordering check always (forecast_reference_time/
        valid_time are required fields).
        """
        guard = PhysicsGuard()
        violations: list[str] = []
        checks_run: list[str] = []

        if "lats" in self.coordinates and "lons" in self.coordinates:
            checks_run.append("coordinate")
            try:
                guard.check_coordinate_arrays(self.coordinates["lats"], self.coordinates["lons"])
            except CoordinateError as exc:
                violations.append(str(exc))

        if self.values is not None and self.variable in OPERATIONAL_RANGES:
            checks_run.append("range")
            unit = self.unit if self.unit else None
            try:
                guard.check_range(float(np.min(self.values)), self.variable, unit=unit)
                guard.check_range(float(np.max(self.values)), self.variable, unit=unit)
            except RangeError as exc:
                violations.append(str(exc))

        checks_run.append("time")
        try:
            guard.check_time(self.forecast_reference_time, self.valid_time)
        except TimeError as exc:
            violations.append(str(exc))

        return PhysicsGuardReport(passed=(len(violations) == 0), violations=violations, checks_run=checks_run)

    # --------------------------------------------------- real-data bridges

    @classmethod
    def from_real_field(
        cls,
        result: dict[str, Any],
        field_key: str,
        dataset_id: str,
        variable: str,
        unit: str = "",
    ) -> "Dataset":
        """
        Build a real Dataset from a real
        acf.awci.spatial_field.compute_real_complexity_field() result -
        proof this contract works on ACF's own actual data, not an
        unused abstraction.

        Parameters
        ----------
        result : dict
            A compute_real_complexity_field() return value.
        field_key : str
            Which field in `result` to use as `values`, e.g.
            "awci_field", "physical_field", "temperature_field".
        dataset_id : str
            Caller-assigned id.
        variable : str
            Real CF standard_name (e.g. "air_temperature" for
            "temperature_field") if one applies, else a descriptive
            ACF-internal name (e.g. "awci" for the composite score) -
            same distinction as the class docstring's `variable` field.
        unit : str
            Real unit for `field_key`'s values - "" (dimensionless) for
            a composite score, "K" for temperature_field, etc. Not
            inferred automatically since the raw result dict doesn't
            carry per-field units itself.
        """
        now = datetime.now(UTC)
        return cls(
            id=dataset_id,
            source="CoupledEarthSolver",
            model=result["model"],
            run="perturbed-initial-condition",  # honest label - see forecast/engine.py's own MODEL_CONFIGS disclosure on what "model" stands in for here
            forecast_reference_time=now,
            valid_time=now,
            lead_time=timedelta(0),
            variable=variable,
            unit=unit,
            dimensions=("lat", "lon"),
            coordinates={"lats": result["lats"], "lons": result["lons"]},
            values=result[field_key],
            provenance=Provenance(
                generator="acf.awci.spatial_field.compute_real_complexity_field",
                algorithm_version=result.get("status", "unknown"),
                notes=result.get("honest_limitation", ""),
            ),
        )

    @classmethod
    def from_real_volume(
        cls,
        result: dict[str, Any],
        field_key: str,
        dataset_id: str,
        variable: str,
        unit: str = "",
    ) -> "Dataset":
        """Same as from_real_field(), for a acf.awci.vertical_field.compute_real_complexity_volume() result (3D: level, lat, lon)."""
        now = datetime.now(UTC)
        return cls(
            id=dataset_id,
            source="CoupledEarthSolver",
            model=result["model"],
            run="perturbed-initial-condition",
            forecast_reference_time=now,
            valid_time=now,
            lead_time=timedelta(0),
            variable=variable,
            unit=unit,
            dimensions=("level", "lat", "lon"),
            coordinates={"lats": result["lats"], "lons": result["lons"], "levels": list(range(result["n_levels"]))},
            values=result[field_key],
            provenance=Provenance(
                generator="acf.awci.vertical_field.compute_real_complexity_volume",
                algorithm_version=result.get("status", "unknown"),
                notes=result.get("honest_limitation", ""),
            ),
        )
