"""
Physics-Informed AI Models Architecture Encyclopedia Module
"""

from typing import Any, Dict


class PhysicsInformedAIArchitectures:
    """
    Spécifications des modèles d'IA scientifique hybrides (PINN, FNO, GNN).
    """

    @staticmethod
    def pinn_loss_formulation(data_loss: float, pde_residual_loss: float, lambda_pde: float = 1.0) -> float:
        """Loss_PINN = Loss_Data + lambda_pde * Loss_PDE_Residual."""
        return data_loss + lambda_pde * pde_residual_loss

    @staticmethod
    def fourier_neural_operator_specs() -> Dict[str, Any]:
        """Retourne les métadonnées de l'architecture FNO."""
        return {
            "name": "Fourier Neural Operator (FNO)",
            "domain": "Apprentissage d'opérateurs pour EDP atmosphériques",
            "resolution_invariant": True,
            "speedup_vs_nwp": "1000x - 10000x",
            "references": ["Li et al. (2020) NeurIPS", "FourCastNet / GraphCast"],
        }
