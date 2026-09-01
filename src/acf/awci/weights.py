"""
AWCI Weights Manager
====================

Manages weights for each module contributing to AWCI.
"""


class WeightsManager:
    """
    Manages weights for AWCI module contributions.

    Default weights are based on expert knowledge and can be
    adjusted during calibration phase.
    """

    DEFAULT_WEIGHTS = {
        "dynamic": 0.20,
        "thermodynamic": 0.25,
        "convective": 0.20,
        "microphysical": 0.15,
        "topographic": 0.10,
        "temporal": 0.05,
        "confidence": 0.05,
    }

    def __init__(self, weights: dict[str, float] | None = None):
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
        Set weight for a specific module, proportionally rescaling every
        other weight so the total still sums to 1.0.

        NOTE (correction): this used to set only the requested weight
        and then validate that ALL weights summed to 1.0 - which fails
        for virtually any real single-weight change, since the other
        modules' weights are left untouched (e.g. raising "dynamic"
        from 0.20 to 0.30 leaves the other 6 weights as-is, so the
        total becomes 1.10 and _validate_weights() raises immediately).
        The method could never succeed for its own stated purpose. It
        now redistributes the remaining budget (1 - value) across the
        other weights proportionally to their current share, so the
        total stays at 1.0.

        Note: To set several weights to specific chosen values at once
        (without this proportional rescaling of the rest), use
        update_weights() instead.
        """
        if value < 0 or value > 1:
            raise ValueError(f"Weight must be between 0 and 1. Got: {value}")

        others = {m: w for m, w in self.weights.items() if m != module}
        others_total = sum(others.values())
        remaining = 1.0 - value
        if others_total > 0:
            scale = remaining / others_total
            for m in others:
                self.weights[m] = others[m] * scale
        self.weights[module] = value
        self._validate_weights()

    def update_weights(self, updates: dict[str, float]):
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

    def get_all_weights(self) -> dict[str, float]:
        """Get all weights."""
        return self.weights.copy()

    def reset(self):
        """Reset to default weights."""
        self.weights = self.DEFAULT_WEIGHTS.copy()
