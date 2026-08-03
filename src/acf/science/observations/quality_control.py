"""
Operational Meteorological Observation Quality Control (QC) Algorithms Module
"""

import math
from typing import List, Tuple


class ObservationQCFlags:
    """Codes de contrôle qualité normalisés (WMO WIGOS Quality Flags)."""
    PASSED = 0
    SUSPECT = 1
    FAILED = 2
    NOT_CHECKED = 9


def gross_error_check(value: float, min_val: float, max_val: float) -> int:
    """Test de limites absolues physiques (Gross Error Check)."""
    if math.isnan(value):
        return ObservationQCFlags.FAILED
    if min_val <= value <= max_val:
        return ObservationQCFlags.PASSED
    return ObservationQCFlags.FAILED


def range_check(value: float, min_clim: float, max_clim: float) -> int:
    """Test de vraisemblance climatologique (Climatological Range Check)."""
    if gross_error_check(value, min_clim, max_clim) == ObservationQCFlags.PASSED:
        return ObservationQCFlags.PASSED
    return ObservationQCFlags.SUSPECT


def temporal_consistency_check(val_t2: float, val_t1: float, delta_t_sec: float, max_rate_per_sec: float) -> int:
    """Test de cohérence temporelle de la variation de la mesure (Rate of Change Check)."""
    if delta_t_sec <= 0.0 or math.isnan(val_t2) or math.isnan(val_t1):
        return ObservationQCFlags.NOT_CHECKED
    rate = abs(val_t2 - val_t1) / delta_t_sec
    if rate <= max_rate_per_sec:
        return ObservationQCFlags.PASSED
    return ObservationQCFlags.FAILED


def background_check(obs_val: float, model_bg_val: float, obs_error: float, bg_error: float, threshold_sigma: float = 3.0) -> Tuple[int, float]:
    """
    Test du premier deviné par rapport au modèle NWP (Background Check / Innovation Check).
    Rejette l'observation si |y - H(x_b)| > threshold_sigma * sqrt(sigma_o^2 + sigma_b^2).
    """
    innovation = obs_val - model_bg_val
    total_std = math.sqrt(obs_error**2 + bg_error**2)
    if total_std <= 0.0:
        return ObservationQCFlags.FAILED, innovation

    normalized_res = abs(innovation) / total_std
    if normalized_res <= threshold_sigma:
        return ObservationQCFlags.PASSED, innovation
    return ObservationQCFlags.FAILED, innovation


def buddy_check(obs_val: float, neighbor_vals: List[float], max_allowed_diff_std: float = 2.5) -> int:
    """Test des voisins proches (Buddy Check / Spatial Consistency)."""
    if not neighbor_vals:
        return ObservationQCFlags.NOT_CHECKED

    valid_neighbors = [v for v in neighbor_vals if not math.isnan(v)]
    if not valid_neighbors:
        return ObservationQCFlags.NOT_CHECKED

    mean_n = sum(valid_neighbors) / len(valid_neighbors)
    variance_n = sum((v - mean_n)**2 for v in valid_neighbors) / len(valid_neighbors)
    std_n = math.sqrt(variance_n) if variance_n > 1e-6 else 1.0

    if abs(obs_val - mean_n) <= max_allowed_diff_std * std_n:
        return ObservationQCFlags.PASSED
    return ObservationQCFlags.SUSPECT
