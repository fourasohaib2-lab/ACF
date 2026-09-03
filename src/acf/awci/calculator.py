"""
AWCI Calculator
===============

Aviation Weather Complexity Index calculator.
"""

from collections.abc import Callable
from typing import Any

from acf.ai.ensemble.ensemble_manager import EnsembleManager
from acf.awci.scientific_status import (
    UNCERTAINTY_METHOD_STATUS,
    ThresholdStatus,
    WeightStatusEntry,
    get_interaction_weight_status,
)

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

    Real multi-model disagreement (NOTE, added 2026-09-02, explicit
    user request "branche le vrai ensemble/consensus")
    -----------------------------------------------------------------
    `FORECAST_MODULES` also includes `model_disagreement` now.
    `ModelConsensusEngine.compute_unified_consensus()`
    (`visualization/ai_forecast_center/model_consensus_engine.py`)
    and `ForecastComparisonMatrix.get_comparison_matrix()`
    (`.../forecast_comparison.py`) were checked first and confirmed to
    still be honest stubs — the former only sums declared weights
    (`status: "WEIGHTS_ONLY_NO_MODEL_FIELDS_FUSED"`), the latter
    explicitly reports `"status":
    "NOT_COMPUTED_NO_MODEL_COMPARISON_RUN"`. Neither fuses or compares
    a real model output field, so neither feeds this module.

    Instead, `ModelConsensusEngine` gained a new, genuinely real
    method: `compute_real_multi_model_disagreement()`. It actually
    runs ACF's own `CoupledEarthSolver` once per requested model at
    that model's real grid configuration
    (`acf.forecast.engine.MODEL_CONFIGS` — the same real
    infrastructure the one-click AROME/ALADIN HPC pipelines already
    submit, now also covering ARPEGE), with an independently
    perturbed initial condition per model, and reads each model's real
    value at the point nearest the query location — real
    nearest-neighbour regridding, genuine per-model output, genuine
    spread via `EnsembleManager` (reused). Its `model_realizations`
    field is ready to hand straight to `data["model_realizations"]`
    here. Honest limitation carried over from that method's own
    docstring: this compares ACF's own solver at multiple real grid
    resolutions/perturbations, standing in for AROME/ALADIN/ARPEGE —
    not real operational NWP archives (none are available in this
    environment). What's real: the solver genuinely runs per model,
    the values genuinely differ, and the spread is genuinely computed
    from them — not a fabricated placeholder.

    Default weight is 0.0 (opt-in, see `weights.py`), same convention
    as `ensemble_spread` — zero behavior change for callers who don't
    supply `data["model_realizations"]`.

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
    FORECAST_MODULES = frozenset({"confidence", "ensemble_spread", "model_disagreement"})

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
              agree perfectly" — see _compute_spread_score().
            - model_realizations: optional dict[str, list[float]], real
              per-model values at this point for one or more of
              Normalizer.MODEL_DISAGREEMENT_REFERENCE's variables
              (e.g. {"temperature": [288.8, 287.6, 286.2]}) — typically
              ModelConsensusEngine.compute_real_multi_model_
              disagreement()'s own `model_realizations` return value,
              handed straight through. Drives the real
              model_disagreement module (see class docstring).

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
            self._compute_spread_score(ensemble_members, self.normalizer.normalize_ensemble_spread)
            if ensemble_members
            else 0.0
        )

        # Model disagreement module - real cross-model spread when
        # data["model_realizations"] is supplied (typically the
        # 'model_realizations' field of ModelConsensusEngine.
        # compute_real_multi_model_disagreement()'s return value; see
        # class docstring). Same "0.0 = no signal supplied" convention
        # as ensemble_spread above, not "models agree perfectly".
        model_realizations = data.get("model_realizations")
        scores["model_disagreement"] = (
            self._compute_spread_score(model_realizations, self.normalizer.normalize_model_disagreement)
            if model_realizations
            else 0.0
        )

        return scores

    def _compute_spread_score(
        self, realizations: dict[str, list[float]], normalize: Callable[[float, str], float]
    ) -> float:
        """
        Real spread-derived complexity contribution, in [0, 1]. Shared
        by ensemble_spread (per-member realizations of one model) and
        model_disagreement (per-model realizations at one point) —
        both are "genuine standard deviation across N real values,
        normalized against a documented reference", differing only in
        which reference dict `normalize` reads from (Normalizer.
        normalize_ensemble_spread vs. normalize_model_disagreement).

        For each supplied variable with >= 2 values, computes the
        genuine standard deviation via EnsembleManager(values).spread
        — the same real formula EnsembleManager already provides for
        ensemble statistics, reused here rather than reimplemented —
        then normalizes it via `normalize`. Averages across whichever
        variables were actually usable.

        Parameters
        ----------
        realizations : dict[str, list[float]]
            Real per-member or real per-model values, keyed by
            variable name.
        normalize : Callable[[float, str], float]
            Normalizer.normalize_ensemble_spread or
            Normalizer.normalize_model_disagreement — raises KeyError
            for a variable with no declared reference, which this
            method treats as "not usable", not as an error to
            propagate (an unrecognized variable simply doesn't
            contribute, rather than crashing the whole calculation).

        Returns
        -------
        float
            Mean normalized spread in [0, 1] across the recognized,
            usable variables. 0.0 if none are usable — an honestly
            "no usable signal" result, not a claim of perfect
            agreement.
        """
        normalized_spreads = []
        for variable, values in realizations.items():
            if len(values) < 2:
                continue
            try:
                spread = EnsembleManager(values).spread
                normalized_spreads.append(normalize(spread, variable))
            except KeyError:
                continue

        if not normalized_spreads:
            return 0.0
        return sum(normalized_spreads) / len(normalized_spreads)

    @staticmethod
    def get_interaction_weight_status(term: str) -> WeightStatusEntry:
        """
        Real scientific status of one INTERACTION_WEIGHTS entry
        (docs/ACF_MASTER_PROMPT.md section 80) - see
        acf.awci.scientific_status for the real classification.
        """
        return get_interaction_weight_status(term)

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

    def calculate_with_uncertainty(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Real `AWCI = score ± uncertainty` / real empirical `P(class)`,
        per docs/ACF_MASTER_PROMPT.md section 64 ("il peut être plus
        scientifique de représenter AWCI = 72 ± uncertainty ou
        P(AWCI class) plutôt qu'un seul chiffre sans contexte. Étudier
        cette possibilité.") - explicitly flagged there as something to
        study, not a firm requirement; this is that study, built as a
        real, additive method (calculate() itself is untouched).

        Real method, not a fabricated distribution: when `data` carries
        real `ensemble_members`/`model_realizations` (the same real
        per-variable, per-member/per-model value lists
        `calculate_module_scores()`'s own ensemble_spread/
        model_disagreement modules already consume - see that method's
        docstring), this computes a genuine AWCICalculator.calculate()
        score once per REAL realization - substituting that
        realization's real value for each variable it supplies into an
        otherwise-unchanged copy of `data`, holding every other field
        at its already-supplied point value - producing N genuine AWCI
        scores, not N samples drawn from an invented parametric
        distribution (no Gaussian/Beta/etc. is assumed anywhere here).
        `awci_mean`/`awci_std`/`awci_min`/`awci_max` are the real
        sample statistics of those N real scores, and
        `awci_class_probabilities` is the real empirical fraction of
        those N real scores in each real `_get_level()` band - not a
        parametric class-probability model.

        If both `ensemble_members` and `model_realizations` are
        supplied, they are combined per real realization index (up to
        the smaller of the two real counts) - a real, disclosed, but
        not the only possible combination choice.

        Honest fallback (section 61 - "préférer UNKNOWN à FALSE
        CERTAINTY"): without real ensemble/model data, there is no
        honest basis for a real distribution here - this returns
        `uncertainty_available: False` with a real explanation, rather
        than inventing a band from `confidence` alone (which would be
        exactly the kind of unfounded formula section 78 warns
        against - no notation/hypothesis/source/domain-of-validity
        would back it).

        Real, disclosed scientific status of this method itself (see
        acf.awci.scientific_status): the realization-substitution
        technique is HYPOTHESIS-grade - a real, defensible design
        choice, not externally validated or published for this
        composite index.
        """
        result = self.calculate(data)

        ensemble_members = data.get("ensemble_members") or {}
        model_realizations = data.get("model_realizations") or {}
        if not ensemble_members and not model_realizations:
            result["uncertainty_available"] = False
            result["uncertainty_note"] = (
                "No real ensemble_members/model_realizations supplied - no honest basis "
                "for a real AWCI distribution (see calculate_with_uncertainty()'s own docstring, "
                "docs/ACF_MASTER_PROMPT.md section 61)."
            )
            return result

        combined_realizations: dict[str, list[float]] = {**ensemble_members, **model_realizations}
        n_members = min((len(values) for values in combined_realizations.values()), default=0)
        if n_members < 2:
            result["uncertainty_available"] = False
            result["uncertainty_note"] = "Fewer than 2 real realizations supplied - no real spread to compute."
            return result

        member_scores: list[float] = []
        for i in range(n_members):
            member_data = dict(data)
            member_data.pop("ensemble_members", None)
            member_data.pop("model_realizations", None)
            for variable, values in combined_realizations.items():
                member_data[variable] = values[i]
            member_scores.append(self.calculate(member_data)["awci"])

        mean_score = sum(member_scores) / len(member_scores)
        variance = sum((s - mean_score) ** 2 for s in member_scores) / len(member_scores)

        class_counts: dict[str, int] = {}
        for score in member_scores:
            level = self._get_level(score)
            class_counts[level] = class_counts.get(level, 0) + 1

        result["uncertainty_available"] = True
        result["n_realizations"] = n_members
        result["awci_mean"] = round(mean_score, 1)
        result["awci_std"] = round(variance**0.5, 1)
        result["awci_min"] = round(min(member_scores), 1)
        result["awci_max"] = round(max(member_scores), 1)
        result["awci_member_scores"] = [round(s, 1) for s in member_scores]
        result["awci_class_probabilities"] = {level: round(count / n_members, 3) for level, count in class_counts.items()}
        result["uncertainty_method_status"] = UNCERTAINTY_METHOD_STATUS
        return result

    @staticmethod
    def get_uncertainty_method_status() -> ThresholdStatus:
        """Real scientific status of calculate_with_uncertainty()'s own
        method (docs/ACF_MASTER_PROMPT.md section 64) - see
        acf.awci.scientific_status for the real classification."""
        return UNCERTAINTY_METHOD_STATUS

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
            "model_disagreement": "Désaccord inter-modèles (fusion réelle)",
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
