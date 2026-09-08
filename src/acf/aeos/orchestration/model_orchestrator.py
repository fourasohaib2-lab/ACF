"""
Atmospheric Complexity Framework (ACF)

AEOS Model Orchestration Module (Phase 8)
(ModelOrchestrator, ModelExecutionPlan, ModelConsensus driving IFS, AROME, ICON, GraphCast, Pangu, NeuralGCM, AIFS)
"""

from dataclasses import dataclass


@dataclass
class ModelExecutionPlan:
    """Plan d'exécution d'un modèle NWP ou d'IA."""

    model_name: str
    grid_resolution_km: float | None
    vertical_levels: int | None
    target_horizon_hours: int | None
    compute_nodes: int | None
    is_real_data: bool = False


@dataclass
class ModelConsensus:
    """Consensus calculé entre les modèles NWP déterministes et d'IA stochastiques."""

    variable: str
    ensemble_mean: float | None
    ensemble_spread: float | None
    consensus_level: str
    is_real_data: bool = False


class ModelOrchestrator:
    """
    Orchestrateur universel de modèles numériques et d'IA (IFS, AROME, ICON, WRF, GraphCast, Pangu, FourCastNet, NeuralGCM, AIFS).
    """

    SUPPORTED_MODELS = ["IFS", "AROME", "ICON", "WRF", "GraphCast", "FourCastNet", "Pangu", "NeuralGCM", "AIFS"]

    @classmethod
    def create_execution_plan(cls, model_name: str = "GraphCast") -> ModelExecutionPlan:
        """
        Génère un plan d'exécution optimisé pour un modèle donné.

        NOTE (correction): model_name was genuinely validated/echoed,
        but grid_resolution_km/vertical_levels/target_horizon_hours/
        compute_nodes used to return the identical fixed
        (25.0, 37, 240, 4) for ANY of the 9 supported models - IFS
        (~9km), AROME (~1.3km), ICON (~13km) and GraphCast (~0.25°)
        have genuinely different real resolutions, so a single fixed
        plan cannot be "optimized for a given model" as claimed. No
        real per-model deployment-planning capability exists yet in
        ACF. Not fabricated.
        """
        if model_name not in cls.SUPPORTED_MODELS:
            model_name = "GraphCast"

        return ModelExecutionPlan(
            model_name=model_name,
            grid_resolution_km=None,
            vertical_levels=None,
            target_horizon_hours=None,
            compute_nodes=None,
            is_real_data=False,
        )

    @classmethod
    def evaluate_model_consensus(cls, variable: str = "2m_temperature") -> ModelConsensus:
        """
        Calcule le consensus d'ensemble entre les 9 modèles orchestrés.

        NOTE (correction): variable was genuinely echoed, but this used
        to unconditionally claim a fixed ensemble_mean=18.4/
        ensemble_spread=0.35/"HIGH CONSENSUS" regardless of variable,
        with 0 real outputs ever gathered from any of the 9 orchestrated
        models (IFS/AROME/ICON/WRF/GraphCast/FourCastNet/Pangu/
        NeuralGCM/AIFS are not actually run anywhere in this codebase).
        Not fabricated.
        """
        return ModelConsensus(
            variable=variable,
            ensemble_mean=None,
            ensemble_spread=None,
            consensus_level="NOT_COMPUTED_NO_MODEL_OUTPUTS_CONNECTED",
            is_real_data=False,
        )
