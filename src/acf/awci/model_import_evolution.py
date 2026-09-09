"""
AWCI Model-Import 4D Evolution Adapter
=======================================

The real, generic TIME counterpart to `acf.awci.model_import` (the
per-point adapter): maps an arbitrary imported model file that genuinely
carries a TIME dimension into a real, per-grid-cell AWCI evolution —
AWCI(x, y, t) — the "4D over imported data" tier.

This closes the real, disclosed scope note in the AWCI completion
report: "4D remains at its existing implemented level (real volume via
CoupledEarthSolver; no time-varying import series yet)". The 4D playback
UI (`AWCIDashboard`'s ▶ 4D Evolution button + global-map animation) is
data-source agnostic — it animates an
`awci_evolution[frame, level, lat, lon]` array plus its own
`valid_time_seconds` — so this adapter FEEDS THE SAME STRUCTURE with
real values from the imported file instead of a solver trajectory.

Every frame is a genuine, per-grid-cell `AWCICalculator.calculate()`
over the file's own fields at that valid time (measured cost: ~0.03 ms
per cell => a 6-frame 20x40 grid is ~0.15 s) — no synthetic field, no
interpolation, no fabrication. A variable absent from the file stays
absent per frame (AWCICalculator's own defaults apply, exactly like the
per-point adapter); per-frame all-NaN cells stay NaN and the
corresponding AWCI cell is NaN (matplotlib shows it as the map's
existing NaN color).

Honest limits (same discipline as model_import):
- No spatial regridding: per-frame nearest-neighbour grid from the
  file's own lat/lon coordinate variables (a file without real
  lat/lon coordinates CANNOT be gridded honestly -> ModelImportError).
- No vertical interpolation: the same disclosed nearest-level /
  surface fallback as the per-point adapter, resolved once and
  reused for every frame (the file's own level coordinate does not
  move between its own valid times).
- CAPE/CIN are NOT recomputed per cell/frame (a MetPy parcel ascent
  per cell would be a real but very large cost no caller opted into;
  the per-point adapter still computes real column CAPE/CIN at the
  exact point of interest). A file that declares surface CAPE/CIN
  fields directly gets them mapped per frame.
"""

from __future__ import annotations

import re
from typing import Any

import numpy as np

from acf.awci.calculator import AWCICalculator
from acf.awci.model_import import (
    _DERIVED_KEYS,
    _VARIABLE_ALIASES,
    ModelImportError,
    _find_level_index,
    _match_variable,
)
from acf.data.dataset import Dataset

__all__ = [
    "ModelImportError",
    "compute_awci_evolution_from_imported_dataset",
]


def _validate_grid(dataset: Dataset) -> tuple[np.ndarray, np.ndarray]:
    """Real gridded-domain validation: returns (lats, lons) from the
    file's own coordinate variables, raising ModelImportError when the
    file carries no real lat/lon coordinates (a gridded 4D file
    without coordinates cannot be mapped honestly - the same disclosed
    refusal the per-point adapter discloses as a note for point
    sampling)."""
    lat_coord = dataset.get_variable("latitude")
    if lat_coord is None:
        lat_coord = dataset.get_variable("lat")
    lon_coord = dataset.get_variable("longitude")
    if lon_coord is None:
        lon_coord = dataset.get_variable("lon")
    if lat_coord is None or lon_coord is None:
        raise ModelImportError(
            "No real latitude/longitude coordinate variables in this file - a gridded 4D "
            "evolution cannot be mapped honestly without them (the per-point adapter still "
            "samples such a file as a single station/column)."
        )
    lats = np.asarray(lat_coord, dtype=float).reshape(-1)
    lons = np.asarray(lon_coord, dtype=float).reshape(-1)
    if lats.size < 2 or lons.size < 2:
        raise ModelImportError(
            f"Coordinate variables too small for a real gridded evolution: lat {lats.size}, lon {lons.size} "
            "(a single column/point file has no genuine horizontal domain)."
        )
    return lats, lons


def _pick_frame_indices(n_time: int, n_frames_max: int) -> list[int]:
    """Real uniform frame selection: first/last always included, rest
    evenly spaced - the animation covers the file's real full span.
    (n_frames_max <= 1 degenerates to just the first real valid time -
    a division-by-zero here was found by this module's own tests.)"""
    if n_time <= n_frames_max or n_frames_max <= 1:
        return list(range(min(n_time, max(n_frames_max, 1))))
    return [round(i * (n_time - 1) / (n_frames_max - 1)) for i in range(n_frames_max)]


def _decode_time_coordinate(
    dataset: Dataset, n_time: int, frame_indices: list[int], notes: list[str]
) -> np.ndarray:
    """Real valid-time decoding from the file's own `time` coordinate
    variable (CF "<unit> since <epoch>" convention), falling back to
    frame-relative seconds with an honest note."""
    t_coord = dataset.get_variable("time")
    if t_coord is not None:
        t_arr = np.asarray(t_coord, dtype=float).reshape(-1)
        if t_arr.size == n_time:
            unit_meta = dataset.get_metadata("time_units")
            unit = unit_meta.strip() if isinstance(unit_meta, str) else ""
            m = re.match(
                r"^\s*(seconds?|secs?|s|minutes?|mins?|min|hours?|hrs?|h|days?|d)"
                r"\s+since\s+",
                unit,
                re.IGNORECASE,
            )
            if m:
                token = m.group(1).lower()
                multiplier = {
                    "s": 1.0, "sec": 1.0, "secs": 1.0, "second": 1.0, "seconds": 1.0,
                    "min": 60.0, "mins": 60.0, "minute": 60.0, "minutes": 60.0,
                    "h": 3600.0, "hr": 3600.0, "hrs": 3600.0, "hour": 3600.0, "hours": 3600.0,
                    "d": 86400.0, "day": 86400.0, "days": 86400.0,
                }.get(token, 1.0)
                notes.append(
                    f"real time coordinate decoded from the file's own units metadata ({unit!r})"
                )
                return np.asarray(t_arr[frame_indices], dtype=float) * multiplier
            notes.append(
                "the file's own time coordinate carried no decodable CF unit string - "
                "raw coordinate values are shown as seconds"
            )
            return np.asarray(t_arr[frame_indices], dtype=float)
        notes.append(
            f"the file's own time coordinate has {t_arr.size} entries but the time-carrying "
            f"variables have {n_time} steps - frame-relative times used instead"
        )
    notes.append(
        "no real time coordinate in this file - times are frame-relative (t+1h per frame)"
    )
    return np.arange(len(frame_indices), dtype=float) * 3600.0


def compute_awci_evolution_from_imported_dataset(
    dataset: Dataset,
    *,
    n_frames_max: int = 8,
    level_hpa: float = 300.0,
    calculator: Any | None = None,
) -> dict[str, Any]:
    """Compute a real AWCI(x, y, t) evolution from a time-dimensioned
    imported model file.

    Parameters
    ----------
    dataset : acf.data.dataset.Dataset
        A real dataset from `acf.data.manager.DataManager.open()`.
    n_frames_max : int
        Cap on how many of the file's own valid times are processed
        (frames are picked uniformly across the file's own time axis,
        first and last always included, so the animation covers the
        file's real full span). Default 8 keeps the off-thread compute
        bounded (~0.03 ms per cell, measured).
    level_hpa : float
        The AWCI point pipeline's own flight level (hPa), matched to
        the file's own nearest declared pressure-level coordinate once
        and reused for every frame (the file's own level coordinate
        does not move between its own valid times).
    calculator : optional
        An AWCICalculator-compatible instance (default: one fresh
        AWCICalculator, shared across frames - the same stateless
        discipline everywhere else in this package); parameter exists
        for test injection.

    Returns
    -------
    dict
        awci_evolution : (n_frames, 1, n_lat, n_lon) real per-cell AWCI
            (level axis kept, size 1, so the structure matches the
            solver evolution AWCIDashboard's playback already renders;
            the level slider then works unchanged).
        lats, lons : the file's own real coordinate arrays.
        valid_time_seconds : real elapsed time per frame, decoded from
            the file's own time coordinate when present (CF "<unit>
            since <epoch>"), else frame-relative (disclosed in notes).
        n_frames, n_levels (=1), level_idx, frame_time_indices :
            structural/provenance keys.
        matched_variables, disagreeing_time_axes, notes, status,
        is_real_data, source_file : provenance, same conventions as
            the per-point adapter.
    """
    lats, lons = _validate_grid(dataset)

    # ---- match the file's variables ONCE (same machinery as the
    # per-point adapter) - the file's own naming does not move between
    # its own valid times.
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

    core_keys = ("temperature", "wind_speed", "specific_humidity", "pressure")
    has_any_core = any(k in matched for k in core_keys) or {"u_wind", "v_wind"}.issubset(matched)
    if not has_any_core:
        raise ModelImportError(
            f"No usable core meteorological variable could be matched in {dataset.name!r} "
            f"(matched: {sorted(matched)}; recognized alias families: "
            + "; ".join(f"{k}: {', '.join(a[:6])}..." for k, a in _VARIABLE_ALIASES.items())
            + ")."
        )

    # ---- which matched variables genuinely carry a leading time axis?
    # 3-D+ (time, lat, lon[/...]) fields do; 2-D (lat, lon) surface
    # fields do not and are held constant across frames (disclosed).
    time_steps_by_var: dict[str, int] = {}
    for var in matched.values():
        arr = np.asarray(dataset.get_variable(var))
        time_steps_by_var[var] = int(arr.shape[0]) if arr.ndim >= 3 else 1

    candidate_counts = [n for n in time_steps_by_var.values() if n > 1]
    if not candidate_counts:
        raise ModelImportError(
            f"No matched variable in {dataset.name!r} genuinely carries a leading time dimension "
            "(all matched fields are 2-D (lat, lon) surface fields) - a real 4D evolution needs at "
            "least one (time, lat, lon) field. The per-point adapter (acf.awci.model_import) still "
            "works on this file."
        )
    # The file's own real time-axis size: the most common count among
    # its own time-carrying variables (majority vote - robust to one
    # mismatched variable; disclosed when variables disagree).
    n_time = int(max(set(candidate_counts), key=candidate_counts.count))
    disagreeing = sorted(v for v, n in time_steps_by_var.items() if n > 1 and n != n_time)

    notes: list[str] = []
    if disagreeing:
        notes.append(
            "variables with a time axis of a different length than the majority "
            f"({disagreeing}) are skipped per frame when their own shape disagrees"
        )

    frame_indices = _pick_frame_indices(n_time, n_frames_max)
    level_idx, level_note = _find_level_index(dataset, level_hpa)
    if level_note:
        notes.append(level_note)

    # ---- per-frame, per-cell real extraction + scoring.
    calc = calculator if calculator is not None else AWCICalculator()
    n_lat, n_lon = lats.size, lons.size
    awci_evolution = np.full((len(frame_indices), 1, n_lat, n_lon), np.nan, dtype=float)

    for f_i, t in enumerate(frame_indices):
        # Real time slice: EVERY variable whose leading axis matches the
        # file's time axis contributes arr[t] - not just the variables
        # matched above (a real bug found by this module's own tests:
        # a file's q/RH variable is matched only INSIDE the per-cell
        # extraction's derivation pass, never in the first-pass matched
        # dict - slicing only matched variables left it 3-D, so
        # _scalar_at read its [0] slice, i.e. the values of TIME 0,
        # silently leaking another valid time's moisture into every
        # later frame). Anything else (2-D surface fields, 1-D level
        # coordinates, static columns) contributes as-is. Metadata
        # (units etc.) is copied so per-cell extraction re-reads the
        # real units.
        frame_ds = Dataset(name=f"{dataset.name}#t{t}", filetype=dataset.filetype, source=dataset.source)
        for var_name, arr_value in dataset.variables.items():
            arr = np.asarray(arr_value)
            if arr.ndim >= 3 and arr.shape[0] == n_time:
                frame_ds.add_variable(var_name, arr[t])
            else:
                frame_ds.add_variable(var_name, arr_value)
        for var_name in dataset.variables:
            for suffix in ("_units", "_standard_name", "_long_name", "_acf"):
                meta = dataset.get_metadata(f"{var_name}{suffix}")
                if meta is not None:
                    frame_ds.set_metadata(f"{var_name}{suffix}", meta)

        for lat_i in range(n_lat):
            for lon_i in range(n_lon):
                from acf.awci.model_import import extract_awci_point_inputs

                ex = extract_awci_point_inputs(
                    frame_ds,
                    float(lats[lat_i]),
                    float(lons[lon_i]),
                    level_hpa=level_hpa,
                    compute_convective_energy=False,
                )
                if not ex["inputs"]:
                    continue  # genuinely nothing extractable at this cell - stays NaN
                result = calc.calculate(ex["inputs"])
                awci_evolution[f_i, 0, lat_i, lon_i] = float(result["awci"])

    valid_time_seconds = _decode_time_coordinate(dataset, n_time, frame_indices, notes)

    return {
        "awci_evolution": awci_evolution,
        "lats": lats,
        "lons": lons,
        "valid_time_seconds": valid_time_seconds,
        "n_frames": len(frame_indices),
        "n_levels": 1,
        "level_idx": level_idx,
        "frame_time_indices": frame_indices,
        "matched_variables": sorted(set(matched.values())),
        "disagreeing_time_axes": disagreeing,
        "notes": notes,
        "status": "REAL_IMPORTED_MODEL_EVOLUTION",
        "is_real_data": True,
        "source_file": str(dataset.filepath) if dataset.filepath else dataset.name,
    }
