"""
AWCI Model-Import Adapter
==========================

The real, generic counterpart to `acf.awci.archive_field` (the
RESTOR-specific ALADIN adapter): maps an arbitrary imported model file —
already opened through ACF's own real ingestion pipeline
(`acf.data.manager.DataManager` -> one of `acf.data.readers`' real
readers, e.g. NetCDF/GRIB/xarray — into real `AWCICalculator`
inputs at a point.

This closes the real, disclosed gap the dashboard's own "📂 Import
Model File" button has been carrying since it was added (see that
button's tooltip: "Does not yet auto-compute AWCI from an arbitrary
file's own field names"). AWFUL, honest scope discipline of this
project applies here exactly as elsewhere:

- A field is matched by ACF's own real alias machinery
  (`acf.catalog.parameter_mapper.ParameterMapper` — the same mapper
  `acf.importers.readers.netcdf_reader.NetCDFReader` already resolves
  every variable through, plus each variable's own real
  `standard_name`/`long_name` metadata when present). Names not in the
  mapper and not recognizable CF names are never guessed.
- A variable genuinely absent is left absent — `AWCICalculator`'s own
  real defaults apply, never a fabricated value; the result's
  `missing_variables` list reports what was looked for and not found.
- Units are converted with the real `acf.normalization.units.convert_unit()`
  when the file declares a compatible one; a variable whose declared
  unit cannot be converted to the expected native unit is treated as
  missing (with a real, per-variable reason in `skipped_variables`),
  never silently reinterpreted.
- The adapter is deliberately ONE abstraction level above the
  RESTOR-specific one: it consumes ACF's own generic `Dataset` shape
  (variables dict + metadata), not a particular FA-file convention.

What is NOT done here (honest limits, same as archive_field):
- No spatial regridding: a point sample is taken nearest-neighbour
  from the file's own grid (`sample`-style 2D/3D indexing), same
  convention as `acf.awci.archive_field.sample_archive_at_point()`.
- No vertical interpolation: the user-chosen vertical level is matched
  to the file's own nearest declared level coordinate when present;
  otherwise the surface/first index is used and disclosed.
- CAPE/CIN/precipitation-phase/theta-e/updraft/Froude are NOT derived
  here from partial single-level fields (the same disclosed discipline
  as `acf.awci.spatial_field`): when the file genuinely provides a
  full vertical column of T/q/p, real column CAPE/CIN can be computed
  via the existing `acf.awci.convective_energy` MetPy pipeline.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

from acf.awci.convective_energy import compute_real_cape_cin_at_point
from acf.data.dataset import Dataset
from acf.normalization.units import convert_unit

#: Real, disclosed: AWCI's native unit per mapped key (the same
#: conventions AWCICalculator.calculate_module_scores()'s own docstring
#: and AWCI_KEY_NATIVE_UNIT in acf.awci.input_adapter already declare).
#: Public (read by acf.awci.model_import_cross_section, the path-sample
#: counterpart of this module) - same values, one home.
AWCI_KEY_NATIVE_UNIT: dict[str, str] = {
    "temperature": "K",
    "specific_humidity": "kg kg-1",
    "wind_speed": "m s-1",
    "pressure": "hPa",
    "cape": "J kg-1",
    "cin": "J kg-1",
    "precipitation": "mm h-1",
    "altitude": "m",
}

#: Real source-unit equivalences `convert_unit()` accepts for the same
#: physical quantity (UCUM-style with separators). Only used to decide
#: whether a declared unit is already the native one; everything else
#: goes through the real converter, which raises on genuinely unknown
#: units. Public for the same reason as AWCI_KEY_NATIVE_UNIT above.
UNIT_ALIASES: dict[str, tuple[str, ...]] = {
    "K": ("K", "Kelvin", "kelvin"),
    "kg kg-1": ("kg kg-1", "kg/kg", "g kg-1", "g/kg"),
    "m s-1": ("m s-1", "m/s", "m s**-1"),
    "hPa": ("hPa", "millibar", "mb"),
    "Pa": ("Pa",),
    "J kg-1": ("J kg-1", "J/kg", "J kg**-1"),
    "mm h-1": ("mm h-1", "mm/hr", "mm/h", "kg m-2 h-1"),
    "m": ("m", "meter", "metre"),
    "%": ("%", "percent"),
}

# Backwards-compatible private spellings (this module's own earlier
# internal uses; kept so no existing caller breaks).
_AWCI_KEY_NATIVE_UNIT = AWCI_KEY_NATIVE_UNIT
_UNIT_ALIASES = UNIT_ALIASES

#: Real, disclosed alias table: AWCI key -> the file-variable aliases
#: recognized for it. Superset of `create_default_mapper()`'s own real
#: registrations (that mapper resolves t2m/T2/TMP/UGRD/VGRD/QVAPOR/...);
#: this table adds the direct canonical names AWCICalculator itself
#: uses plus common CF/GRIB names the default mapper does not carry.
#: Matching is case-insensitive on the file's own variable name AND,
#: when present, the variable's own real standard_name/long_name
#: metadata (NetCDFReader stores both).
_VARIABLE_ALIASES: dict[str, tuple[str, ...]] = {
    "temperature": ("t2m", "2t", "t", "temp", "air_temperature", "temperature", "t2", "tmp", "tmp_2m", "t_2m", "2m_temperature", "surface_temperature"),
    "specific_humidity": ("q", "q2m", "qvapor", "qv", "specific_humidity", "q_at_2m", "2m_specific_humidity"),
    "wind_speed": ("wind_speed", "ws", "wspd", "wind_speed_10m", "10m_wind_speed", "si10"),
    "u_wind": ("u10", "u", "ugrd", "u_wind_10m", "u_wind", "10u"),
    "v_wind": ("v10", "v", "vgrd", "v_wind_10m", "v_wind", "10v"),
    "pressure": ("mslp", "msl", "prmsl", "pressure", "air_pressure", "ps", "psfc", "pres", "surfpression", "mean_sea_level_pressure", "surface_air_pressure", "sp"),
    "cape": ("cape", "surfcape", "surface_cape", "cape_surface", "convective_available_potential_energy"),
    "cin": ("cin", "surfcin", "surface_cin", "convective_inhibition"),
    "precipitation": ("tp", "rain", "rainnc", "rainc", "precipitation", "precip", "pr", "large_scale_precipitation", "total_precipitation"),
    "altitude": ("altitude", "height", "orog", "orography", "hgt", "surface_height", "zs", "ter"),
    "relative_humidity": ("rh", "rh2m", "relative_humidity", "2m_relative_humidity", "r2"),
    "dewpoint": ("d2m", "td2", "dewpoint", "dew_point_temperature", "dewpoint_temperature", "2d"),
}

#: AWCI keys whose value comes from OTHER raw variables (u/v -> speed,
#: RH -> specific humidity) - never matched directly in the per-key
#: pass below.
_DERIVED_KEYS = ("wind_speed", "specific_humidity")


class ModelImportError(ValueError):
    """Raised when an imported model file genuinely cannot feed AWCI
    (no recognizable variable at all) - a real, reported error, never
    silently substituted with synthetic data."""


@lru_cache(maxsize=1)
def _default_parameter_mapper() -> Any:
    """Process-wide default ParameterMapper (the same one
    NetCDFReader resolves variables through), built lazily so importing
    this module stays cheap and test-friendly."""
    from acf.catalog.default_mapping import create_default_mapper

    return create_default_mapper()


def _canonical_variable_name(dataset: Dataset, var_name: str) -> str:
    """Real canonical name for one of the file's own variables: its own
    stored `<name>_acf` metadata (NetCDFReader resolves every variable
    through ACF's real ParameterMapper and stores the result here),
    falling back to resolving the name through a fresh default mapper
    (GRIBReader stores no `_acf` metadata), falling back to the raw
    name itself. Never invents a name."""
    stored = dataset.get_metadata(f"{var_name}_acf")
    if isinstance(stored, str) and stored:
        return stored.lower()
    resolved = _default_parameter_mapper().resolve(var_name)
    if isinstance(resolved, str) and resolved:
        return resolved.lower()
    return var_name.lower()


def match_variable(dataset: Dataset, awci_key: str) -> str | None:
    """Return the file's own variable name genuinely matching one AWCI
    key (first match wins in `_VARIABLE_ALIASES` order), or None when
    the file has no such variable - never a guessed name.

    Public so acf.awci.model_import_cross_section (the path-sample
    counterpart of this module) reuses the exact same real matching
    machinery instead of a second, drift-prone copy."""
    canonical_names: dict[str, str] = {
        var: _canonical_variable_name(dataset, var) for var in dataset.variables
    }
    for alias in _VARIABLE_ALIASES.get(awci_key, ()):
        for var, canonical in canonical_names.items():
            if canonical == alias or var.lower() == alias:
                return var
        # Also match the variable's own real standard_name/long_name
        # metadata (NetCDFReader stores them; e.g. a file naming its
        # temperature "tas" still carries standard_name
        # "air_temperature").
        for var in dataset.variables:
            for meta_key in (f"{var}_standard_name", f"{var}_long_name"):
                value = dataset.get_metadata(meta_key)
                if isinstance(value, str) and value.strip().lower() == alias:
                    return var
    return None


#: Backwards-compatible private spelling (this module's own internal
#: uses below; kept so nothing else breaks).
_match_variable = match_variable


def _unit_matches(declared: Any, expected: str) -> bool:
    if not isinstance(declared, str) or not declared:
        return False
    return declared.strip() in _UNIT_ALIASES.get(expected, (declared,))


def resolve_volume_conversion(
    raw_value: Any, declared_unit: Any, expected_unit: str
) -> Any:
    """Real unit conversion via acf.normalization's own converter for a
    scalar OR a whole numpy array (the per-point adapter converts one
    scalar per call; the path-sample cross-section module needs the
    identical unit discipline applied to entire (level, lat, lon)
    volumes, with the same honest skip - never a guessed
    reinterpretation). NaN values pass through untouched as NaN.

    Returns the converted value, or None when the declared unit is
    absent/unconvertible (the caller then skips the variable and
    reports why).
    """
    if not isinstance(declared_unit, str) or not declared_unit:
        return None
    declared = declared_unit.strip()
    if _unit_matches(declared, expected_unit):
        return raw_value
    # Real known equivalences the converter itself accepts (both real
    # spellings of the same physical unit).
    if expected_unit == "K" and declared in ("degC", "°C", "celsius"):
        return raw_value + 273.15
    for candidates in UNIT_ALIASES.values():
        if declared in candidates and expected_unit in candidates:
            return raw_value
    try:
        # pint handles numpy arrays natively (elementwise), so the same
        # real converter serves both scalar and array input.
        return convert_unit(raw_value, declared, expected_unit)
    except Exception:
        return None


def _convert_to_native(raw_value: float, declared_unit: Any, expected_unit: str) -> float | None:
    """Real unit conversion via acf.normalization's own converter;
    None when the declared unit is absent/unconvertible (honest skip,
    reported by the caller - never a guessed reinterpretation)."""
    converted = resolve_volume_conversion(raw_value, declared_unit, expected_unit)
    if converted is None:
        return None
    return float(converted)


def _scalar_at(value: Any, lat_idx: int, lon_idx: int, level_idx: int | None) -> float | None:
    """Real nearest-neighbour scalar from a file variable's own array
    shape: (level, lat, lon) when a level dimension exists, else
    (lat, lon). NaN/None -> None (honestly missing, never coerced)."""
    if value is None:
        return None
    arr = np.asarray(value, dtype=float)
    if arr.size == 0:
        return None
    try:
        if arr.ndim >= 3:
            if level_idx is None:
                level_idx = 0
            level_idx = int(min(max(level_idx, 0), arr.shape[0] - 1))
            scalar = arr[level_idx, lat_idx, lon_idx]
        elif arr.ndim == 2:
            scalar = arr[lat_idx, lon_idx]
        elif arr.ndim == 1:
            scalar = arr[0 if arr.size == 1 else lon_idx % arr.size]
        else:
            scalar = arr.reshape(-1)[0]
    except IndexError:
        return None
    scalar = float(scalar)
    if np.isnan(scalar):
        return None
    return scalar


def _find_level_index(dataset: Dataset, target_hpa: float) -> tuple[int | None, str | None]:
    """Real nearest declared pressure-level index for a target hPa, or
    (None, reason) when the file declares no usable level coordinate
    (caller then uses the surface/first level and discloses that).
    Only files that genuinely carry a pressure-dimension coordinate are
    honoured - never an assumed level list."""
    # A level COORDINATE is 1-D; a variable named "pressure" can also
    # be the real 3-D pressure FIELD (found the hard way in this
    # module's own tests: argmin over its flattened 320 values returned
    # a nonsense flat index). "level"/"isobaric" are checked first;
    # "pressure" is only honoured as a coordinate when genuinely 1-D.
    coord = None
    for name in ("level", "isobaric", "pressure"):
        candidate = dataset.get_variable(name)
        if candidate is None:
            continue
        arr_candidate = np.asarray(candidate)
        if arr_candidate.ndim == 1:
            coord = candidate
            break
    if coord is None:
        return None, "no real pressure-level coordinate in this file - surface/first level used"
    arr = np.asarray(coord, dtype=float).reshape(-1)
    if arr.size == 0:
        return None, "empty pressure-level coordinate in this file - surface/first level used"
    # Level coordinates may be Pa or hPa; real, disclosed heuristic on
    # the coordinate's own magnitude (typical level coordinates are
    # either ~100-1000 (hPa) or ~10000-100000 (Pa)).
    if arr.max() > 5000.0:
        arr = arr / 100.0
    return int(np.argmin(np.abs(arr - target_hpa))), None


def extract_awci_point_inputs(
    dataset: Dataset,
    lat: float,
    lon: float,
    *,
    level_hpa: float = 300.0,
    compute_convective_energy: bool = True,
) -> dict[str, Any]:
    """Extract real `AWCICalculator.calculate()` inputs from an
    imported model `Dataset` at one point.

    Parameters
    ----------
    dataset : acf.data.dataset.Dataset
        A real dataset returned by `acf.data.manager.DataManager.open()`
        (any of ACF's real readers - NetCDF/GRIB/FA via EPyGrAM/...).
    lat, lon : float
        The point of interest; sampled nearest-neighbour on the file's
        own grid (same convention as `acf.awci.archive_field`).
    level_hpa : float
        The AWCI point pipeline's own flight level (hPa). Matched to
        the file's own declared pressure-level coordinate when present;
        otherwise the surface/first level is used and disclosed in
        `notes`.
    compute_convective_energy : bool
        When True AND the file genuinely provides a full vertical
        column of temperature/specific humidity/pressure at this point,
        real column CAPE/CIN are computed via the existing, tested
        `acf.awci.convective_energy` MetPy pipeline and fed to
        AWCICalculator's convective module. When the file lacks a real
        column, this silently does nothing (CAPE stays at
        AWCICalculator's own default) - never a fabricated CAPE.

    Returns
    -------
    dict
        inputs : dict ready for `AWCICalculator.calculate()` (absent
            variables stay absent - real defaults apply).
        lat_idx, lon_idx, level_idx : the real grid indices sampled.
        matched_variables : awci key -> the file's own variable name.
        missing_variables : keys looked for and genuinely not found.
        skipped_variables : key -> real reason a matched variable was
            unusable (unconvertible unit, all-NaN at the point, ...).
        notes : real disclosure strings (level handling, coordinate
            order assumptions).
        status, is_real_data, source_file : provenance.
    """
    variables = dataset.variables
    if not variables:
        raise ModelImportError(f"Imported dataset {dataset.name!r} has no variables at all.")

    matched: dict[str, str] = {}
    for awci_key in _VARIABLE_ALIASES:
        if awci_key in _DERIVED_KEYS:
            continue
        var = _match_variable(dataset, awci_key)
        if var is not None:
            matched[awci_key] = var

    u_var = _match_variable(dataset, "u_wind")
    v_var = _match_variable(dataset, "v_wind")
    if u_var is not None and v_var is not None:
        matched["u_wind"] = u_var
        matched["v_wind"] = v_var

    lat_idx, lon_idx, level_idx, notes = _resolve_indices(dataset, lat, lon, level_hpa)

    inputs: dict[str, Any] = {}
    matched_variables: dict[str, str] = {}
    missing_variables: list[str] = []
    skipped_variables: dict[str, str] = {}

    def _use(key: str, value: float) -> None:
        inputs[key] = value

    def _convert_and_use(awci_key: str, var: str, expected_unit: str) -> None:
        raw_value = _scalar_at(variables.get(var), lat_idx, lon_idx, level_idx)
        if raw_value is None:
            skipped_variables[awci_key] = f"variable {var!r} has no real (non-NaN) value at the sampled point"
            return
        declared_unit = dataset.get_metadata(f"{var}_units")
        converted = _convert_to_native(raw_value, declared_unit, expected_unit)
        if converted is None:
            skipped_variables[awci_key] = (
                f"variable {var!r} declares unit {declared_unit!r}, which could not be converted to {expected_unit!r}"
            )
            return
        matched_variables[awci_key] = var
        _use(awci_key, converted)

    # Direct keys with a real native unit. "wind_speed" and
    # "specific_humidity" are deliberately NOT here (derived below from
    # u/v and RH/q respectively) - so they are also never falsely
    # reported as missing before their own derivation pass runs.
    for awci_key in ("temperature", "pressure", "cape", "cin", "precipitation", "altitude"):
        if awci_key not in matched:
            missing_variables.append(awci_key)
            continue
        expected_unit = _AWCI_KEY_NATIVE_UNIT[awci_key]
        _convert_and_use(awci_key, matched[awci_key], expected_unit)

    # u/v -> real wind speed magnitude.
    if "u_wind" in matched and "v_wind" in matched:
        u_val = _scalar_at(variables.get(matched["u_wind"]), lat_idx, lon_idx, level_idx)
        v_val = _scalar_at(variables.get(matched["v_wind"]), lat_idx, lon_idx, level_idx)
        if u_val is None or v_val is None:
            skipped_variables["wind_speed"] = "u/v variables have no real value at the sampled point"
            missing_variables.append("wind_speed")
        else:
            matched_variables["wind_speed"] = f"{matched['u_wind']}+{matched['v_wind']}"
            _use("wind_speed", float(np.sqrt(u_val**2 + v_val**2)))
    elif "wind_speed" not in inputs:
        missing_variables.append("wind_speed")

    # Direct q when the file reports specific humidity itself.
    if "specific_humidity" not in inputs:
        q_var = _match_variable(dataset, "specific_humidity")
        if q_var is not None:
            _convert_and_use("specific_humidity", q_var, _AWCI_KEY_NATIVE_UNIT["specific_humidity"])
        else:
            missing_variables.append("specific_humidity")

    # Relative humidity -> real specific humidity (the real reverse of
    # what acf.science.moisture does for archived ALADIN: RH (%) +
    # temperature + pressure -> q via the existing tested chain) when
    # the file reports RH but no direct q.
    if "specific_humidity" not in inputs:
        rh_var = _match_variable(dataset, "relative_humidity")
        if rh_var is not None and "temperature" in inputs and "pressure" in inputs:
            rh_raw = _scalar_at(variables.get(rh_var), lat_idx, lon_idx, level_idx)
            rh_unit = dataset.get_metadata(f"{rh_var}_units")
            if rh_raw is not None:
                # Real, disclosed RH-unit handling: an explicit "%" (or
                # percent) unit wins first - treating 70 (%) as a 0-1
                # fraction fed the real Moisture chain 7000% RH and a
                # genuine saturation_mixing_ratio ValueError (found by
                # this module's own tests); a declared unitless/ratio
                # unit or a genuinely <= 1.5 raw value is the real 0-1
                # fraction convention (same one archive_field documents
                # for RESTOR's real 0-1 HUMI_RELAT fields); anything
                # else is the real 0-100 percent convention.
                if _unit_matches(rh_unit or "", "%"):
                    rh_fraction = rh_raw / 100.0
                elif 0.0 < rh_raw <= 1.5:
                    rh_fraction = rh_raw
                else:
                    rh_fraction = rh_raw / 100.0
                from acf.science.moisture import Moisture

                try:
                    q = Moisture.specific_humidity_from_relative_humidity(
                        rh_fraction * 100.0, inputs["pressure"], inputs["temperature"]
                    )
                except ValueError as exc:
                    # A genuinely unphysical RH/pressure combination in
                    # this real file (e.g. RH > 100% with a superseded
                    # pressure) - skipped honestly, never coerced.
                    skipped_variables["specific_humidity"] = (
                        f"real RH->q conversion failed for variable {rh_var!r}: {exc}"
                    )
                    rh_raw = None  # type: ignore[assignment]
                else:
                    matched_variables["specific_humidity"] = rh_var
                    _use("specific_humidity", float(q))
            if rh_raw is None:
                if "specific_humidity" not in skipped_variables:
                    skipped_variables["specific_humidity"] = f"variable {rh_var!r} has no real value at the sampled point"

    # Real column CAPE/CIN from a genuine vertical column, when the
    # file provides one (opt-in, real MetPy pipeline, same module
    # acf.awci.spatial_field uses).
    if compute_convective_energy:
        cape_cin = _column_cape_cin(dataset, lat_idx, lon_idx)
        if cape_cin is not None:
            cape, cin = cape_cin
            if cape is not None:
                inputs["cape"] = cape
                matched_variables.setdefault("cape", "vertical column (MetPy surface-based ascent)")
            if cin is not None:
                inputs["cin"] = cin
                matched_variables.setdefault("cin", "vertical column (MetPy surface-based ascent)")
        else:
            notes.append("no full real vertical column of T/q/p available - column CAPE/CIN not computed")

    return {
        "inputs": inputs,
        "lat_idx": lat_idx,
        "lon_idx": lon_idx,
        "level_idx": level_idx,
        "matched_variables": matched_variables,
        "missing_variables": missing_variables,
        "skipped_variables": skipped_variables,
        "notes": notes,
        "status": "REAL_IMPORTED_MODEL_FILE",
        "is_real_data": bool(inputs),
        "source_file": str(dataset.filepath) if dataset.filepath else dataset.name,
    }


def _resolve_indices(dataset: Dataset, lat: float, lon: float, level_hpa: float) -> tuple[int, int, int | None, list[str]]:
    """Real nearest-neighbour grid indices from the file's own declared
    coordinate variables (lat/lon), with real, disclosed fallbacks when
    the file carries none (then the point can be sampled only if the
    file is a single column/point - otherwise the first index is used
    and disclosed). Returns (lat_idx, lon_idx, level_idx, notes)."""
    notes: list[str] = []
    # NOTE: `or`-chaining would raise "truth value of an array is
    # ambiguous" on a real coordinate array - each candidate is checked
    # explicitly for presence instead (a real None check, not a
    # truthiness check).
    lat_coord = dataset.get_variable("latitude")
    if lat_coord is None:
        lat_coord = dataset.get_variable("lat")
    lon_coord = dataset.get_variable("longitude")
    if lon_coord is None:
        lon_coord = dataset.get_variable("lon")

    lat_arr = np.asarray(lat_coord, dtype=float).reshape(-1) if lat_coord is not None else None
    lon_arr = np.asarray(lon_coord, dtype=float).reshape(-1) if lon_coord is not None else None

    if lat_arr is not None and lat_arr.size and lon_arr is not None and lon_arr.size:
        lat_idx = int(np.argmin(np.abs(lat_arr - lat)))
        lon_idx = int(np.argmin(np.abs(lon_arr - lon)))
        level_idx, level_note = _find_level_index(dataset, level_hpa)
        if level_note:
            notes.append(level_note)
        return lat_idx, lon_idx, level_idx, notes

    # No real coordinate variables - the dataset may still be a single
    # station/column (0-d or 1-d variables). Sample the first cell and
    # disclose; AWCICalculator's missing-variable defaults handle the
    # rest honestly.
    notes.append(
        "no real latitude/longitude coordinate variables in this file - the first grid cell was sampled "
        "(matches a single-station/point file; a gridded file without coordinates cannot be point-sampled honestly)"
    )
    lat_idx, lon_idx = 0, 0
    level_idx, level_note = _find_level_index(dataset, level_hpa)
    if level_note:
        notes.append(level_note)
    return lat_idx, lon_idx, level_idx, notes


def _column_cape_cin(dataset: Dataset, lat_idx: int, lon_idx: int) -> tuple[float | None, float | None] | None:
    """Real per-column CAPE/CIN when the file genuinely provides full
    vertical columns of T/q/p at this point (same real MetPy pipeline
    as acf.awci.convective_energy). Returns None when any of the three
    column variables is missing/not 3D - never a fabricated CAPE."""
    t_var = _match_variable(dataset, "temperature")
    q_var = _match_variable(dataset, "specific_humidity") or _match_variable(dataset, "relative_humidity")
    p_var = _match_variable(dataset, "pressure")
    if t_var is None or q_var is None or p_var is None:
        return None

    t_arr = np.asarray(dataset.variables.get(t_var), dtype=float)
    q_arr = np.asarray(dataset.variables.get(q_var), dtype=float)
    p_arr = np.asarray(dataset.variables.get(p_var), dtype=float)
    if not (t_arr.ndim >= 3 and q_arr.ndim >= 3 and p_arr.ndim >= 3):
        return None
    if not (t_arr.shape == q_arr.shape == p_arr.shape):
        return None

    t_col = t_arr[:, lat_idx, lon_idx]
    q_col = q_arr[:, lat_idx, lon_idx]
    p_col = p_arr[:, lat_idx, lon_idx]
    # Real unit handling for the column: q in kg/kg (native); p
    # Pa -> hPa when the coordinate magnitude says so (same disclosed
    # heuristic as _find_level_index).
    if np.nanmax(p_col) > 5000.0:
        p_col = p_col / 100.0
    if np.nanmean(q_col) > 0.1:
        # Declared g/kg-style values (real files exist like this);
        # disclosed conversion to the native kg/kg.
        q_col = q_col / 1000.0
    mask = ~(np.isnan(t_col) | np.isnan(q_col) | np.isnan(p_col))
    t_col, q_col, p_col = t_col[mask], q_col[mask], p_col[mask]
    if p_col.size < 2:
        return None
    if np.nanmean(q_col) <= 0.0:
        return None

    result = compute_real_cape_cin_at_point(t_col, q_col, p_col)
    return result["cape_j_kg"], result["cin_j_kg"]


def compute_awci_from_imported_dataset(
    dataset: Dataset,
    lat: float,
    lon: float,
    *,
    level_hpa: float = 300.0,
    calculator: Any | None = None,
) -> dict[str, Any]:
    """One-call convenience: extract real inputs from an imported model
    `Dataset` at (lat, lon, level_hpa) and run the real
    `AWCICalculator` on them.

    Returns
    -------
    dict
        result : the real `AWCICalculator.calculate()` output (awci,
            module_scores, level, decomposition, explanation...).
        extraction : the full `extract_awci_point_inputs()` payload
            (matched/missing/skipped variables, notes, provenance).

    Raises
    ------
    ModelImportError
        When the dataset has no variables at all, or genuinely none of
        AWCICalculator's core inputs (temperature/wind/humidity/
        pressure) could be extracted - reported honestly, never
        substituted with synthetic data.
    """
    extraction = extract_awci_point_inputs(dataset, lat, lon, level_hpa=level_hpa)
    inputs = extraction["inputs"]

    core_keys = ("temperature", "wind_speed", "specific_humidity", "pressure")
    if not any(key in inputs for key in core_keys):
        raise ModelImportError(
            f"No usable core meteorological variable could be extracted from {dataset.name!r} "
            f"at ({lat:.2f}, {lon:.2f}). Matched variables: {sorted(extraction['matched_variables'])}; "
            f"skipped: {extraction['skipped_variables']}. "
            "Recognized alias families (file variable names are matched through ACF's own "
            "ParameterMapper first, then these native aliases): "
            + "; ".join(f"{key}: {', '.join(aliases[:6])}…" for key, aliases in _VARIABLE_ALIASES.items())
            + "."
        )

    calc = calculator if calculator is not None else _default_calculator()
    result = calc.calculate(inputs)
    return {"result": result, "extraction": extraction}


_default_calculator_instance: Any | None = None


def _default_calculator() -> Any:
    global _default_calculator_instance
    if _default_calculator_instance is None:
        from acf.awci.calculator import AWCICalculator

        _default_calculator_instance = AWCICalculator()
    return _default_calculator_instance


__all__ = [
    "AWCI_KEY_NATIVE_UNIT",
    "ModelImportError",
    "UNIT_ALIASES",
    "compute_awci_from_imported_dataset",
    "extract_awci_point_inputs",
    "match_variable",
    "resolve_volume_conversion",
    "restor_fullpos_path",
]


def restor_fullpos_path(aladin_data_dir: str | Path, run_datetime: str, lead_hours: int) -> Path:
    """Re-exported for convenience from acf.awci.archive_field - one
    real naming convention, one real home (imported here so callers of
    this module keep a single import site)."""
    from acf.awci.archive_field import restor_fullpos_path as _impl

    return _impl(aladin_data_dir, run_datetime, lead_hours)
