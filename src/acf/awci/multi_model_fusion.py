"""
ACF Complexity Engine — real full-field multi-model fusion
=============================================================

Explicit user request, closing reports/ACF_MASTER_AUDIT_v2.md's
"Fusion multi-modèles en champ complet (§29-30) : PARTIAL (réel, scopé
point-par-point)" finding.
`acf.visualization.ai_forecast_center.model_consensus_engine.
ModelConsensusEngine.compute_real_multi_model_disagreement()` already
runs the real solver per model and compares real values - but only at
ONE lat/lon point. `compute_unified_consensus()` combines weights, but
never any real model field. Neither produces a fused 2D field.

What's built here
------------------
`compute_real_multi_model_field_fusion()`:
1. Runs `acf.awci.spatial_field.compute_real_complexity_field()` once
   per requested model (same real CoupledEarthSolver infrastructure
   `compute_real_multi_model_disagreement()` already uses), each at
   its own real grid resolution
   (`acf.forecast.engine.MODEL_CONFIGS`) with a distinct, deterministic
   per-model perturbation seed.
2. Regrids every model's real field onto one common target grid via
   real nearest-neighbour lookup (`regrid_nearest_neighbor()` below) -
   same NN convention already used throughout this package
   (`path_sampling.py`, `compute_real_multi_model_disagreement()`'s
   own per-point lookup), not a new interpolation scheme. Honest scope:
   NOT bilinear/conservative regridding - reports/ACF_MASTER_AUDIT_v2.md's
   own "pas de regridding bilinéaire/conservatif générique" finding
   is NOT closed by this module, deliberately - see that function's
   own docstring.
3. Weights each regridded field - real inverse-error weights from a
   `acf.verification.skill_database.ModelSkillDatabase` when it has
   real recorded history for every requested model
   (same all-or-nothing convention `ModelConsensusEngine.
   compute_unified_consensus()` already established, not a new mixing
   rule), otherwise honestly falls back to equal weights.
4. Optionally bias-corrects each model's regridded field using that
   same database's real recorded mean `bias` (from
   `acf.verification.nwp_metrics.NWPVerificationMetrics.evaluate_all()`,
   via `VerificationPipeline`) for that model/variable, before
   combining - the real "biais par modèle" the Prompt Maître's §29-30
   describes. A model with no recorded bias history is combined
   uncorrected, not silently assigned bias=0.
5. Computes a real per-grid-point spread field across the regridded
   models via `acf.ai.ensemble.ensemble_manager.EnsembleManager`
   (reused, not reimplemented) - the full-field equivalent of
   `compute_real_multi_model_disagreement()`'s single-point
   `disagreement_spread`.

Honest limitation, same disclosure as everywhere else the real solver
stands in for real operational archives (see
`compute_real_multi_model_disagreement()`'s own docstring): this
compares ACF's OWN solver run at each model's real grid resolution
with independent per-model perturbations, standing in for AROME/
ALADIN/ARPEGE - not real operational NWP archives (none are available
in this environment).
"""

from __future__ import annotations

from typing import Any

import numpy as np

from acf.ai.ensemble.ensemble_manager import EnsembleManager
from acf.awci.spatial_field import compute_real_complexity_field
from acf.forecast.engine import MODEL_CONFIGS
from acf.verification.skill_database import ModelSkillDatabase

_DEFAULT_MODELS: tuple[str, ...] = ("AROME", "ALADIN", "ARPEGE")


def regrid_nearest_neighbor(
    lats_src: Any,
    lons_src: Any,
    field_src: np.ndarray,
    lats_target: Any,
    lons_target: Any,
) -> np.ndarray:
    """
    Real nearest-neighbour regrid of `field_src` (shape
    (len(lats_src), len(lons_src))) onto `(lats_target, lons_target)`.

    Same technique `acf.awci.path_sampling.sample_field_along_path()`
    already uses per sample point, vectorised across an entire target
    grid instead of a path - not a second implementation, and not
    bilinear/conservative interpolation (honest scope, see this
    module's own docstring).

    Returns
    -------
    numpy.ndarray, shape (len(lats_target), len(lons_target))
    """
    lats_src_arr = np.asarray(lats_src)
    lons_src_arr = np.asarray(lons_src)
    lats_target_arr = np.asarray(lats_target)
    lons_target_arr = np.asarray(lons_target)

    lat_idx = np.argmin(np.abs(lats_target_arr[:, None] - lats_src_arr[None, :]), axis=1)
    lon_idx = np.argmin(np.abs(lons_target_arr[:, None] - lons_src_arr[None, :]), axis=1)
    return field_src[np.ix_(lat_idx, lon_idx)]


def compute_real_multi_model_field_fusion(
    field_key: str = "awci_field",
    models: list[str] | None = None,
    target_model: str | None = None,
    steps: int = 8,
    dt_seconds: float = 60.0,
    perturbation_scale: float = 2.0,
    level: int = 0,
    n_lat: int | None = None,
    n_lon: int | None = None,
    n_levels: int | None = None,
    skill_database: ModelSkillDatabase | None = None,
    variable: str | None = None,
    weight_metric: str = "rmse",
    bias_metric: str = "bias",
) -> dict[str, Any]:
    """
    Real full-field multi-model fusion - see module docstring for the
    5-step pipeline and its honest scope.

    Parameters
    ----------
    field_key : which `compute_real_complexity_field()` field to fuse
        (e.g. "awci_field", "temperature_field", "wind_speed_field").
    models : model names from `acf.forecast.engine.MODEL_CONFIGS`,
        default `("AROME", "ALADIN", "ARPEGE")` - same default set as
        `ModelConsensusEngine.compute_real_multi_model_disagreement()`.
        Must list at least 2.
    target_model : which model's real grid to fuse onto - defaults to
        `models[0]` (explicit, not an arbitrary hidden choice).
    steps, dt_seconds, perturbation_scale, level, n_lat, n_lon, n_levels :
        passed straight through to each model's real
        `compute_real_complexity_field()` call.
    skill_database, variable, weight_metric : if `skill_database` has
        real recorded history (see
        `acf.verification.skill_database.ModelSkillDatabase`) for
        `variable`/`weight_metric` covering every model in `models`,
        those real skill-based weights are used
        (`weight_source="model_skill_database"`); otherwise equal
        weights are used (`weight_source="equal_weights_no_skill_history"`).
    bias_metric : which recorded metric to use as each model's real
        bias correction (default "bias", matching
        `NWPVerificationMetrics.evaluate_all()`'s own key) - only
        applied to a model with real recorded history for it.

    Returns
    -------
    dict
        fused_field : real weighted (and, where real history exists,
            bias-corrected) sum of every model's field, regridded onto
            the target grid.
        spread_field : real per-point multi-model spread (via
            `EnsembleManager.spread`) across the regridded fields.
        target_lats, target_lons : the target grid's real coordinates.
        models_used, target_model, weights, weight_source,
        bias_corrected_models, field_key : real provenance of how
        `fused_field` was produced.
        per_model_fields : each model's own real field, already
            regridded onto the target grid (before weighting/bias
            correction) - so a caller can inspect what went in.
        status, is_real_data, honest_limitation.
    """
    if models is None:
        models = list(_DEFAULT_MODELS)
    if len(models) < 2:
        raise ValueError(f"Need at least 2 models to fuse, got {models}")
    unknown = set(models) - set(MODEL_CONFIGS)
    if unknown:
        raise ValueError(f"Unknown model(s) {sorted(unknown)} - expected among {sorted(MODEL_CONFIGS)}")

    target_model = target_model or models[0]
    if target_model not in models:
        raise ValueError(f"target_model {target_model!r} must be one of models {models}")

    per_model_results: dict[str, dict[str, Any]] = {}
    for i, m in enumerate(models):
        # Distinct, deterministic per-model seed - not derived from a
        # single lat/lon like compute_real_multi_model_disagreement()
        # (there is no single point here), just each model's position
        # in the given list, so repeated calls with the same `models`
        # order reproduce the same per-model perturbation.
        per_model_results[m] = compute_real_complexity_field(
            model=m,
            steps=steps,
            dt_seconds=dt_seconds,
            perturbation_scale=perturbation_scale,
            seed=i,
            level=level,
            n_lat=n_lat,
            n_lon=n_lon,
            n_levels=n_levels,
        )

    target_result = per_model_results[target_model]
    target_lats = target_result["lats"]
    target_lons = target_result["lons"]

    regridded: dict[str, np.ndarray] = {}
    for m, result in per_model_results.items():
        regridded[m] = regrid_nearest_neighbor(result["lats"], result["lons"], result[field_key], target_lats, target_lons)

    weight_source = "equal_weights_no_skill_history"
    weights: dict[str, float] = {m: 1.0 / len(models) for m in models}
    if skill_database is not None and variable is not None:
        skill_weights = skill_database.weights_from_skill(models, variable=variable, metric=weight_metric)
        if len(skill_weights) == len(models):
            weights = skill_weights
            weight_source = "model_skill_database"

    bias_corrected_models: list[str] = []
    corrected: dict[str, np.ndarray] = {}
    for m, field in regridded.items():
        bias = None
        if skill_database is not None and variable is not None:
            bias = skill_database.mean_skill(m, variable, metric=bias_metric)
        if bias is not None:
            corrected[m] = field - bias
            bias_corrected_models.append(m)
        else:
            corrected[m] = field

    fused_field = np.zeros_like(target_result[field_key], dtype=float)
    for m in models:
        fused_field = fused_field + weights[m] * corrected[m]

    stacked = np.stack([corrected[m] for m in models], axis=0)  # (n_models, n_lat, n_lon)
    spread_field = np.zeros(stacked.shape[1:], dtype=float)
    for i in range(stacked.shape[1]):
        for j in range(stacked.shape[2]):
            spread_field[i, j] = EnsembleManager(list(stacked[:, i, j])).spread

    return {
        "fused_field": fused_field,
        "spread_field": spread_field,
        "per_model_fields": regridded,
        "target_lats": target_lats,
        "target_lons": target_lons,
        "target_model": target_model,
        "models_used": models,
        "field_key": field_key,
        "weights": weights,
        "weight_source": weight_source,
        "bias_corrected_models": bias_corrected_models,
        "status": "REAL_MULTI_MODEL_FIELD_FUSION_FROM_ACF_SOLVER",
        "is_real_data": True,
        "honest_limitation": (
            "Each model's field comes from ACF's own CoupledEarthSolver run at that model's real grid "
            "resolution with an independent per-model perturbation, standing in for AROME/ALADIN/ARPEGE - "
            "not real operational NWP archives. Regridding is nearest-neighbour, not bilinear/conservative."
        ),
    }
