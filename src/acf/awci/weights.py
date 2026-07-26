"""
AWCI Weights Manager
====================

Manages weights for each module contributing to AWCI.
"""

from typing import Dict, Optional


class WeightsManager:
    """
    Manages weights for AWCI module contributions.
    
    Default weights are based on expert knowledge and can be
    adjusted during calibration phase.
    """
    
    DEFAULT_WEIGHTS = {
        'dynamic': 0.20,
        'thermodynamic': 0.25,
        'convective': 0.20,
        'microphysical': 0.15,
        'topographic': 0.10,
        'temporal': 0.05,
        'confidence': 0.05,
    }
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        Initialize weights manager.
        
        Parameters
        ----------
        weights : dict, optional
            Custom weights for each module.
            If not provided, uses DEFAULT_WEIGHTS.
        """
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()
        self._validate_weights()
    
    def _validate_weights(self):
        """Validate that weights sum to 1.0."""
        total = sum(self.weights.values())
        if not (0.99 <= total <= 1.01):
            raise ValueError(f"Weights must sum to 1.0. Current sum: {total}")
    
    def get_weight(self, module: str) -> float:
        """Get weight for a specific module."""
        return self.weights.get(module, 0.0)
    
    def set_weight(self, module: str, value: float):
        """
        Set weight for a specific module.
        
        Note: This modifies the weight and immediately validates.
        To change multiple weights at once, use update_weights().
        """
        if value < 0 or value > 1:
            raise ValueError(f"Weight must be between 0 and 1. Got: {value}")
        self.weights[module] = value
        self._validate_weights()
    
    def update_weights(self, updates: Dict[str, float]):
        """
        Update multiple weights at once, then validate.
        
        Parameters
        ----------
        updates : dict
            Dictionary of module: weight pairs to update.
        """
        for module, value in updates.items():
            if value < 0 or value > 1:
                raise ValueError(f"Weight for '{module}' must be between 0 and 1. Got: {value}")
            self.weights[module] = value
        self._validate_weights()
    
    def get_all_weights(self) -> Dict[str, float]:
        """Get all weights."""
        return self.weights.copy()
    
    def reset(self):
        """Reset to default weights."""
        self.weights = self.DEFAULT_WEIGHTS.copy()
