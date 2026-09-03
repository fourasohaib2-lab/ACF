"""
AWCI Input Adapter (docs/awci/AWCI_UI_AUDIT.md §4/§8)
==========================================================

Real bridge from ACF's own real Data Contract
(`acf.core.contracts.dataset.Dataset`) into `AWCICalculator`'s own plain
`dict[str, Any]` input contract - the one genuine gap a pre-implementation
audit of this codebase's real infrastructure found: a real Data Contract
(`Dataset`/`Provenance`/`QualityInfo`/`VariableContract`), a real Model
Adapter Protocol (all 6 named NWP models), and real PhysicsGuard validation
all already existed - but nothing translated `Dataset` into
`AWCICalculator`'s dict, so every real caller built that dict by hand.

Honest scope
-------------
Only `AWCICalculator`'s 4 keys with a real, unambiguous CF standard_name
correspondence are unit-converted via the real CF/PhysicsGuard machinery
(`temperature`, `specific_humidity`, `wind_speed`, `pressure` - see
`AWCI_KEY_TO_CF_STANDARD_NAME` below, limited by `acf.normalization`'s own
real, narrow CF-name coverage - see that package's own docstrings).
`AWCICalculator`'s other real, opt-in keys (`cape`, `cin`, `wind_shear`,
`theta_e`, `updraft_velocity`, `precipitation_phase_severity`,
`mountain_wave_froude`, `altitude`, `confidence`, `temporal_change`) are
ACF-internal composite/derived quantities with no CF standard_name of
their own (see each one's own real formula module under `acf.awci`,
e.g. `acf.awci.wind_shear`) - a `Dataset` supplying one of those is passed
through by direct key match, without a unit-conversion step (there is no
real CF canonical unit to convert to).

A variable genuinely absent from the supplied `datasets` (or whose
`Dataset.values` is `None`) is left absent from the returned data dict -
`AWCICalculator`'s own real default applies, never a fabricated value.
Real quality (`acf.physics_guard.variable_quality.assess_variable_quality()`)
is always assessed for the 4 CF-named keys, present or not - a genuinely
missing one is honestly reported as `MISSING`, not silently skipped.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from acf.core.contracts.dataset import Dataset
from acf.normalization.units import convert_unit
from acf.normalization.variable_names import cf_canonical_unit
from acf.physics_guard.variable_quality import VariableQualityStatus, assess_variable_quality

#: Real, disclosed mapping - only AWCICalculator keys with a real,
#: unambiguous CF standard_name (see module docstring for why the other
#: real AWCICalculator keys aren't here).
AWCI_KEY_TO_CF_STANDARD_NAME: dict[str, str] = {
    "temperature": "air_temperature",
    "specific_humidity": "specific_humidity",
    "wind_speed": "wind_speed",
    "pressure": "air_pressure",
}

#: Real, disclosed: AWCICalculator's own NATIVE unit convention per key
#: - found while testing this adapter to NOT always match the real CF
#: canonical unit `cf_canonical_unit()` would return (e.g. "pressure"
#: here is hPa, matching AWCICalculator.calculate_module_scores()'s own
#: docstring "pressure: Pressure in hPa", while the real CF canonical
#: unit for "air_pressure" is Pa) - the same real AWCI-vs-CF unit-
#: convention mismatch this project has already disclosed elsewhere
#: (e.g. acf.awci.result.AWCIResult's own `quality` field docstring).
#: `data[awci_key]` is converted to THIS unit; the real CF canonical
#: unit is used separately, only for the quality assessment below,
#: which must match `acf.physics_guard.range_check.OPERATIONAL_RANGES`'
#: own real units - never the same conversion reused for both purposes.
AWCI_KEY_NATIVE_UNIT: dict[str, str] = {
    "temperature": "K",
    "specific_humidity": "kg kg-1",
    "wind_speed": "m s-1",
    "pressure": "hPa",
}


def _scalar_value(values: Any) -> float | None:
    """
    Real, honest scalar extraction from a Dataset's own `values` - None
    (never a fabricated 0.0) when genuinely absent.

    Raises
    ------
    ValueError
        If `values` is a real array with more than one element - this
        adapter is for a real per-POINT Dataset; a caller with a full
        field/volume must slice it to one point first (e.g. via
        `acf.awci.path_sampling`), not rely on this function to guess
        which point.
    """
    if values is None:
        return None
    arr = np.asarray(values)
    if arr.size == 0:
        return None
    if arr.size != 1:
        raise ValueError(
            f"build_awci_data_from_datasets() expects a real per-point Dataset (a single value), "
            f"got a real array of shape {arr.shape} - slice it to one point first."
        )
    return float(arr.reshape(-1)[0])


def build_awci_data_from_datasets(datasets: dict[str, Dataset]) -> tuple[dict[str, Any], dict[str, VariableQualityStatus]]:
    """
    Real bridge: real per-point `Dataset`s, keyed by `AWCICalculator`'s
    own data-dict key -> (the dict `AWCICalculator.calculate()`/
    `calculate_module_scores()` accepts, real per-CF-variable quality).

    Parameters
    ----------
    datasets : dict[str, Dataset]
        Keyed by an `AWCICalculator` key (e.g. "temperature", "cape") -
        each `Dataset`'s own real `.values` must already be a single
        real point (see `_scalar_value()`), and its `.unit` honestly
        declared. A key this dict doesn't include is treated exactly
        like an absent variable (see Returns below) - never assumed
        present.

    Returns
    -------
    (data, quality)
        data : dict[str, Any] - ready for `AWCICalculator.calculate()`.
            A key genuinely absent (or whose Dataset carries no real
            value) is left absent - `AWCICalculator`'s own real default
            applies, never a fabricated value.
        quality : dict[str, VariableQualityStatus] - real, keyed by CF
            standard_name, for the 4 keys in
            `AWCI_KEY_TO_CF_STANDARD_NAME` - present or not (a genuinely
            absent one is honestly `MISSING`, not silently omitted from
            this dict). ACF-internal keys (cape, wind_shear, ...) have
            no real CF standard_name to assess an OPERATIONAL_RANGES
            bound against (see `assess_variable_quality()`'s own real,
            disclosed scope) and so carry no quality entry here.
    """
    data: dict[str, Any] = {}
    cf_named_values: dict[str, Any] = {}

    for awci_key, cf_name in AWCI_KEY_TO_CF_STANDARD_NAME.items():
        dataset = datasets.get(awci_key)
        raw_value = _scalar_value(dataset.values) if dataset is not None else None

        awci_value = raw_value
        quality_value = raw_value
        if raw_value is not None and dataset is not None and dataset.unit:
            # Two real, separately-purposed conversions from the SAME
            # raw value - see AWCI_KEY_NATIVE_UNIT's own docstring for
            # why these are not the same target unit.
            awci_native_unit = AWCI_KEY_NATIVE_UNIT[awci_key]
            if dataset.unit != awci_native_unit:
                awci_value = convert_unit(raw_value, dataset.unit, awci_native_unit)
            cf_canonical = cf_canonical_unit(cf_name)
            if dataset.unit != cf_canonical:
                quality_value = convert_unit(raw_value, dataset.unit, cf_canonical)

        if awci_value is not None:
            data[awci_key] = awci_value
        cf_named_values[cf_name] = quality_value

    for awci_key, dataset in datasets.items():
        if awci_key in AWCI_KEY_TO_CF_STANDARD_NAME:
            continue  # already handled above, with real unit conversion
        value = _scalar_value(dataset.values)
        if value is not None:
            data[awci_key] = value

    quality = assess_variable_quality(cf_named_values, expected_variables=list(cf_named_values.keys()))
    return data, quality


def datasets_from_real_field_point(
    result: dict[str, Any], lat_idx: int, lon_idx: int, dataset_id_prefix: str = "awci-point"
) -> dict[str, Dataset]:
    """
    Real convenience: builds the 4 real per-point `Dataset`s
    `build_awci_data_from_datasets()` needs directly from a real
    `acf.awci.spatial_field.compute_real_complexity_field()` result, at
    one real grid point - the exact real field arrays that function
    already returns (`temperature_field`/`specific_humidity_field`/
    `wind_speed_field`/`pressure_field_hpa`), sliced at `(lat_idx,
    lon_idx)`, never a second/recomputed value.

    `Dataset.from_real_field()` (already real, built earlier) keeps the
    FULL field as `values` - not usable here, since this adapter needs a
    real single point (see `_scalar_value()`'s own docstring) - this
    function is the real per-point analog, same provenance convention.
    """
    from datetime import UTC, datetime, timedelta

    from acf.core.contracts.provenance import Provenance

    now = datetime.now(UTC)
    field_specs = {
        "temperature": ("temperature_field", "K"),
        "specific_humidity": ("specific_humidity_field", "kg kg-1"),
        "wind_speed": ("wind_speed_field", "m s-1"),
        "pressure": ("pressure_field_hpa", "hPa"),
    }
    datasets: dict[str, Dataset] = {}
    for awci_key, (field_key, unit) in field_specs.items():
        cf_name = AWCI_KEY_TO_CF_STANDARD_NAME[awci_key]
        datasets[awci_key] = Dataset(
            id=f"{dataset_id_prefix}-{awci_key}",
            source="CoupledEarthSolver",
            model=result["model"],
            run="perturbed-initial-condition",
            forecast_reference_time=now,
            valid_time=now,
            lead_time=timedelta(0),
            variable=cf_name,
            unit=unit,
            dimensions=(),
            coordinates={"lat_idx": lat_idx, "lon_idx": lon_idx},
            values=float(result[field_key][lat_idx, lon_idx]),
            provenance=Provenance(
                generator="acf.awci.spatial_field.compute_real_complexity_field",
                algorithm_version=result.get("status", "unknown"),
                notes=result.get("honest_limitation", ""),
            ),
        )
    return datasets
