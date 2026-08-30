"""
AWCI Calculator
===============

Aviation Weather Complexity Index calculator.
"""

from typing import Any

from .normalizer import Normalizer
from .weights import WeightsManager


class AWCICalculator:
    """
    Aviation Weather Complexity Index (AWCI) calculator.

    Combines multiple atmospheric modules into a single
    complexity score (0-100) with decomposition.

    Interaction terms
    ------------------
    Beyond the linear weighted sum of the 7 independent modules, two
    interaction terms capture non-linear compounding effects that a
    purely additive score misses:

    - wind_topo_interaction  (Vent x Relief): strong wind over complex
      terrain produces disproportionately more turbulence/mountain-
      wave complexity than either factor alone would suggest.
    - conv_thermo_interaction (Convectif x Thermodynamique): strong
      convective potential compounded with strong thermodynamic
      instability increases severe-convection complexity faster than
      a linear sum of the two module scores.

    NOTE: these interaction terms and their weights are an ACF design
    choice for this composite index (AWCI is ACF's own aggregate, not
    a published external standard like EHI/STP) — not derived from an
    external published formula. They are documented here as such, not
    presented as an established literature result.
    """

    # Interaction term weights, additional to the 7 module weights
    # (which independently sum to 1.0). The total weight budget
    # (1.0 + sum(INTERACTION_WEIGHTS)) is used to renormalize the
    # final score back into [0, 1] before scaling to 100, so adding
    # these terms can never push the AWCI score out of [0, 100].
    INTERACTION_WEIGHTS = {
        "wind_topo_interaction": 0.05,
        "conv_thermo_interaction": 0.05,
    }

    def __init__(self, weights: dict[str, float] | None = None):
        """
        Initialize AWCI calculator.

        Parameters
        ----------
        weights : dict, optional
            Custom weights for each module.
            Default weights are used if not provided.
        """
        self.weights_manager = WeightsManager(weights)
        self.normalizer = Normalizer()
        self._last_decomposition: dict[str, float] | None = None

    def calculate_module_scores(self, data: dict[str, Any]) -> dict[str, float]:
        """
        Calculate scores for each module from input data.

        Parameters
        ----------
        data : dict
            Input meteorological data with keys:
            - temperature: Temperature in Kelvin
            - specific_humidity: Specific humidity in kg/kg
            - wind_speed: Wind speed in m/s
            - cape: CAPE in J/kg
            - cin: CIN in J/kg
            - precipitation: Precipitation in mm/h
            - pressure: Pressure in hPa
            - altitude: Altitude in meters
            - confidence: Forecast confidence in %
            - temporal_change: Rate of change

        Returns
        -------
        dict
            Module scores in [0, 1]
        """
        scores = {}

        # Dynamic module - based on wind
        wind = data.get("wind_speed", 0.0)
        scores["dynamic"] = self.normalizer.normalize_wind(wind)

        # Thermodynamic module - based on temperature and humidity
        temp = data.get("temperature", 273.15)
        hum = data.get("specific_humidity", 0.001)

        # Combine temperature and humidity for thermodynamic complexity
        temp_norm = self.normalizer.normalize_temperature(temp)
        hum_norm = self.normalizer.normalize_humidity(hum)
        scores["thermodynamic"] = 0.5 * temp_norm + 0.5 * hum_norm

        # Convective module - based on CAPE and CIN
        cape = data.get("cape", 0.0)
        cin = data.get("cin", 0.0)
        cape_norm = self.normalizer.normalize_cape(cape)
        cin_norm = self.normalizer.normalize_cin(cin)
        scores["convective"] = 0.7 * cape_norm + 0.3 * cin_norm

        # Microphysical module - based on precipitation
        precip = data.get("precipitation", 0.0)
        scores["microphysical"] = self.normalizer.normalize_precipitation(precip)

        # Topographic module - based on altitude
        altitude = data.get("altitude", 0.0)
        scores["topographic"] = self.normalizer.normalize_topographic(altitude)

        # Temporal module - rate of change
        temporal = data.get("temporal_change", 0.0)
        scores["temporal"] = self.normalizer.normalize_temporal(temporal)

        # Confidence module
        confidence = data.get("confidence", 100.0)
        # Lower confidence = higher complexity
        scores["confidence"] = 1.0 - self.normalizer.normalize_confidence(confidence)

        return scores

    def calculate_interaction_scores(self, module_scores: dict[str, float]) -> dict[str, float]:
        """
        Calculate the non-linear interaction terms from module scores.

        Parameters
        ----------
        module_scores : dict
            Output of calculate_module_scores() — each value in [0, 1].

        Returns
        -------
        dict
            Interaction scores in [0, 1], keyed like INTERACTION_WEIGHTS.
        """
        return {
            "wind_topo_interaction": module_scores["dynamic"] * module_scores["topographic"],
            "conv_thermo_interaction": module_scores["convective"] * module_scores["thermodynamic"],
        }

    def calculate(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Calculate AWCI from input data.

        Parameters
        ----------
        data : dict
            Input meteorological data.

        Returns
        -------
        dict
            {
                'awci': float (0-100),
                'decomposition': dict,       # module + interaction contributions, sums to 'awci'
                'level': str,
                'confidence': float,
                'module_scores': dict,
                'interaction_scores': dict,
                'explanation': list[str],    # human-readable, largest contributors first
            }
        """
        # Calculate module scores
        module_scores = self.calculate_module_scores(data)
        interaction_scores = self.calculate_interaction_scores(module_scores)

        # Total weight budget: the 7 module weights (sum to 1.0, enforced
        # by WeightsManager) plus the interaction weights. Dividing by
        # this budget renormalizes the combined weighted sum back into
        # [0, 1] regardless of how many interaction terms are added, so
        # 'awci' is always within [0, 100] and decomposition always sums
        # to it (up to rounding) — no ad hoc clipping needed.
        interaction_weight_total = sum(self.INTERACTION_WEIGHTS.values())
        weight_budget = 1.0 + interaction_weight_total

        weighted_sum = 0.0
        decomposition: dict[str, float] = {}

        for module, score in module_scores.items():
            weight = self.weights_manager.get_weight(module)
            weighted = (score * weight) / weight_budget
            weighted_sum += weighted
            decomposition[module] = round(weighted * 100, 1)

        for term, score in interaction_scores.items():
            weight = self.INTERACTION_WEIGHTS[term]
            weighted = (score * weight) / weight_budget
            weighted_sum += weighted
            decomposition[term] = round(weighted * 100, 1)

        # Scale to 0-100
        awci_score = round(weighted_sum * 100, 1)

        # Determine level
        level = self._get_level(awci_score)

        # Store decomposition for later use
        self._last_decomposition = decomposition

        return {
            "awci": awci_score,
            "decomposition": decomposition,
            "level": level,
            "confidence": data.get("confidence", 100.0),
            "module_scores": {k: round(v * 100, 1) for k, v in module_scores.items()},
            "interaction_scores": {k: round(v * 100, 1) for k, v in interaction_scores.items()},
            "explanation": self._explain(decomposition),
        }

    def _explain(self, decomposition: dict[str, float]) -> list[str]:
        """
        Build a human-readable, largest-contributor-first explanation
        of the decomposition (explainable decomposition).

        Parameters
        ----------
        decomposition : dict
            Output of calculate()'s decomposition (module + interaction
            contributions, in AWCI points).

        Returns
        -------
        list of str
            One sentence per contributor, sorted by contribution
            (largest first), skipping near-zero contributions.
        """
        labels = {
            "dynamic": "Dynamique (vent)",
            "thermodynamic": "Thermodynamique (température/humidité)",
            "convective": "Convectif (CAPE/CIN)",
            "microphysical": "Microphysique (précipitations)",
            "topographic": "Topographique (altitude)",
            "temporal": "Évolution temporelle",
            "confidence": "Incertitude de prévision",
            "wind_topo_interaction": "Interaction Vent x Relief",
            "conv_thermo_interaction": "Interaction Convection x Thermodynamique",
        }

        ranked = sorted(decomposition.items(), key=lambda kv: kv[1], reverse=True)

        explanation = []
        for key, points in ranked:
            if points < 0.5:
                continue
            label = labels.get(key, key)
            explanation.append(f"{label} : {points} points sur 100")

        return explanation

    def _get_level(self, score: float) -> str:
        """
        Determine complexity level from AWCI score.

        Parameters
        ----------
        score : float
            AWCI score (0-100)

        Returns
        -------
        str
            Complexity level
        """
        if score < 20:
            return "Very Low"
        elif score < 35:
            return "Low"
        elif score < 50:
            return "Moderate"
        elif score < 65:
            return "High"
        elif score < 85:
            return "Very High"
        else:
            return "Extreme"

    def get_decomposition(self) -> dict[str, float]:
        """
        Get the decomposition from the last calculation.

        Returns
        -------
        dict
            Decomposition of AWCI by module
        """
        return self._last_decomposition or {}

    def reset(self):
        """Reset the calculator to default state."""
        self._last_decomposition = None
        self.weights_manager.reset()
