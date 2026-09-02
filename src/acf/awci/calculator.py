"""
AWCI Calculator
===============

Aviation Weather Complexity Index calculator.
"""

from typing import Any

from acf.ai.ensemble.ensemble_manager import EnsembleManager

from .normalizer import Normalizer
from .weights import WeightsManager


class AWCICalculator:
    """
    Aviation Weather Complexity Index (AWCI) calculator.

    Combines multiple atmospheric modules into a single
    complexity score (0-100) with decomposition.

    ACF Complexity Engine (docs/ACF_MASTER_UNIFIED_ARCHITECTURE.md,
    layer 17) status
    -----------------------------------------------------------------
    This class is ACF's real, working Complexity Engine core — found
    during the 2026-09-02 architecture audit (docs/
    ACF_ARCHITECTURE_TARGET_GAP_MAP.md flagged `complexity/` as
    entirely absent from the codebase; it was not: it already existed
    here, scoped and named for aviation). Per explicit user decision,
    it is evolved in place rather than duplicated into a new
    top-level package — six GUI panels (`gui/dashboard/awci_*.py`)
    and `gui/esoc/panel_manager.py` already depend on this exact
    class/module path.

    Physical vs. Forecast complexity (NOTE, added 2026-09-02)
    -----------------------------------------------------------------
    The target architecture's own science section is explicit: model
    disagreement/forecast uncertainty is a property of the *forecast*,
    not of the atmosphere itself, and must not be silently averaged
    into a single physical score. Before this change, `confidence`
    was just one more module in the same flat weighted sum as the six
    physical modules — mixing the two dimensions the target
    architecture requires kept separate. `calculate()` now also
    returns `physical_score` and `forecast_score`, each independently
    renormalized to [0, 100] from only the modules in
    `PHYSICAL_MODULES` / `FORECAST_MODULES` respectively (plus the
    interaction terms, which are physical). `awci` / `level` /
    `decomposition` keep their exact prior meaning and formula — no
    behavior change for existing callers.

    Real ensemble spread (NOTE, added 2026-09-02)
    -----------------------------------------------------------------
    `FORECAST_MODULES` now also includes `ensemble_spread`, computed
    from genuine ensemble statistics via
    `acf.ai.ensemble.ensemble_manager.EnsembleManager` (real mean/
    standard-deviation formulas, not a placeholder) when the caller
    supplies `data["ensemble_members"]` — a `dict[str, list[float]]`
    mapping a variable name (one of `Normalizer.
    ENSEMBLE_SPREAD_REFERENCE`'s keys: `cape`, `wind_speed`,
    `temperature`, `precipitation`) to that variable's real per-member
    forecast values at this point. Its default weight is 0.0 (see
    `weights.py`'s `DEFAULT_WEIGHTS`), so every caller that doesn't
    supply ensemble data gets a bit-identical `awci`/`level`/
    `decomposition` to before this module existed — opt in explicitly
    with `update_weights({"ensemble_spread": ..., "confidence": ...})`.

    Multi-model consensus/disagreement — deliberately NOT wired.
    `ModelConsensusEngine` (`visualization/ai_forecast_center/
    model_consensus_engine.py`) and `ForecastComparisonMatrix`
    (`.../forecast_comparison.py`) were checked and are themselves
    honest stubs: the former only sums declared weights and says so
    (`status: "WEIGHTS_ONLY_NO_MODEL_FIELDS_FUSED"`), the latter
    explicitly reports `"status":
    "NOT_COMPUTED_NO_MODEL_COMPARISON_RUN"`, `"is_real_data": False`.
    Neither ever fuses or compares a real model output field anywhere
    in ACF today. Wiring a "model disagreement" module from either
    would mean computing a number from data that does not exist —
    exactly the kind of fabrication this project's audits exist to
    remove, not add. `ensemble_spread` above is real precisely because
    the caller supplies real member values; consensus stays honestly
    absent from `FORECAST_MODULES` until ACF has real multi-model
    field fusion to derive it from.

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
    presented as an established literature result. Both interaction
    terms are physical (they combine two physical modules), so they
    count toward `physical_score`, never `forecast_score`.
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

    # Physical/Forecast classification (see class docstring). Every
    # module produced by calculate_module_scores() must appear in
    # exactly one of these two sets — enforced by a unit test
    # (tests/test_awci_calculator.py) so a future new module can't
    # silently fall into neither/both.
    PHYSICAL_MODULES = frozenset(
        {"dynamic", "thermodynamic", "convective", "microphysical", "topographic", "temporal"}
    )
    FORECAST_MODULES = frozenset({"confidence", "ensemble_spread"})

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
            - ensemble_members: optional dict[str, list[float]], real
              per-member forecast values at this point for one or more
              of Normalizer.ENSEMBLE_SPREAD_REFERENCE's variables
              (e.g. {"cape": [1200, 1800, 900, ...]}). Drives the real
              ensemble_spread module (see class docstring); omitted or
              empty means "no ensemble data supplied", not "models
              agree perfectly" — see _compute_ensemble_spread_score().

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

        # Ensemble spread module - real EnsembleManager statistics when
        # member data is supplied (see class docstring); 0.0 ("no
        # additional signal from this module") otherwise, mirroring how
        # `confidence` above defaults to 100.0 (no evidence of
        # disagreement) rather than assuming the worst.
        ensemble_members = data.get("ensemble_members")
        scores["ensemble_spread"] = (
            self._compute_ensemble_spread_score(ensemble_members) if ensemble_members else 0.0
        )

        return scores

    def _compute_ensemble_spread_score(self, ensemble_members: dict[str, list[float]]) -> float:
        """
        Real ensemble-spread-derived complexity contribution, in
        [0, 1]. For each supplied variable with a declared reference
        spread (Normalizer.ENSEMBLE_SPREAD_REFERENCE) and at least 2
        member values, computes the genuine ensemble standard
        deviation via EnsembleManager(values).spread — the same
        formula EnsembleManager already provides — then normalizes it.
        Averages across whichever variables were actually supplied.

        Parameters
        ----------
        ensemble_members : dict[str, list[float]]
            Real per-member forecast values, keyed by variable name.

        Returns
        -------
        float
            Mean normalized spread in [0, 1] across the recognized,
            usable variables. 0.0 if none of the supplied variables
            are recognized or none has >= 2 members — an honestly
            "no usable ensemble signal" result, not a claim that the
            ensemble genuinely agrees.
        """
        normalized_spreads = []
        for variable, values in ensemble_members.items():
            if variable not in Normalizer.ENSEMBLE_SPREAD_REFERENCE or len(values) < 2:
                continue
            spread = EnsembleManager(values).spread
            normalized_spreads.append(self.normalizer.normalize_ensemble_spread(spread, variable))

        if not normalized_spreads:
            return 0.0
        return sum(normalized_spreads) / len(normalized_spreads)

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

        physical_score = self._renormalized_score(decomposition, self.PHYSICAL_MODULES, include_interactions=True)
        forecast_score = self._renormalized_score(decomposition, self.FORECAST_MODULES, include_interactions=False)

        return {
            "awci": awci_score,
            "decomposition": decomposition,
            "level": level,
            "confidence": data.get("confidence", 100.0),
            "module_scores": {k: round(v * 100, 1) for k, v in module_scores.items()},
            "interaction_scores": {k: round(v * 100, 1) for k, v in interaction_scores.items()},
            "explanation": self._explain(decomposition),
            # Physical vs. Forecast complexity (see class docstring). None
            # when the corresponding modules' weights sum to ~0 — an
            # honestly-undefined renormalization, not a fabricated 0.
            "physical_score": physical_score,
            "forecast_score": forecast_score,
            "physical_level": self._get_level(physical_score) if physical_score is not None else None,
            "forecast_level": self._get_level(forecast_score) if forecast_score is not None else None,
        }

    def _renormalized_score(
        self, decomposition: dict[str, float], module_names: frozenset[str], include_interactions: bool
    ) -> float | None:
        """
        Renormalize the subset of `decomposition` belonging to
        `module_names` (plus the interaction terms if
        `include_interactions`) back into an independent [0, 100]
        score — i.e. "what would the composite score be if only these
        modules existed", not just their raw slice of `awci`.

        Returns None if the selected modules' weight budget is ~0
        (e.g. a caller zeroed every forecast-side weight) — an
        undefined renormalization must not silently read as 0.0
        ("no complexity"), which would be a fabricated result.
        """
        weight_total = sum(self.weights_manager.get_weight(m) for m in module_names)
        points_total = sum(points for name, points in decomposition.items() if name in module_names)

        if include_interactions:
            weight_total += sum(self.INTERACTION_WEIGHTS.values())
            points_total += sum(
                points for name, points in decomposition.items() if name in self.INTERACTION_WEIGHTS
            )

        weight_budget = 1.0 + sum(self.INTERACTION_WEIGHTS.values())
        weight_fraction_of_budget = weight_total / weight_budget

        if weight_fraction_of_budget <= 1e-9:
            return None

        return round(points_total / weight_fraction_of_budget, 1)

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
            "ensemble_spread": "Désaccord d'ensemble (spread réel)",
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
