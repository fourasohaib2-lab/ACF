"""
FireWeatherCalculator: real ACF composite fire-danger index.

See fire_weather/__init__.py's own docstring for the full disclosure
on what this is (an ACF-designed composite of real, physically
understood drivers) and is NOT (a reproduction of Fosberg FWI/Canadian
FWI/McArthur FFDI's specific published coefficients).
"""

from typing import Any

from acf.fire_weather.normalizer import FireWeatherNormalizer

#: Required inputs - no defaults. Fire danger is safety-relevant;
#: silently assuming a "calm" value for a missing temperature/humidity/
#: wind reading (the way AWCICalculator defaults confidence/ensemble
#: inputs to "no additional signal") could mask real risk instead of
#: surfacing that the caller didn't actually supply real data.
_REQUIRED_KEYS = ("temperature", "relative_humidity", "wind_speed")

_LEVELS = [
    (0, "LOW"),
    (20, "MODERATE"),
    (40, "HIGH"),
    (60, "VERY_HIGH"),
    (80, "EXTREME"),
]


class FireWeatherCalculator:
    """
    Composite ACF Fire Weather Index (0-100), from real temperature,
    relative humidity, and wind speed (required), plus an optional
    prolonged-dryness signal (days_since_precipitation).

    See this package's __init__.py docstring for the full honest
    disclosure on scope (ACF's own composite, not a reproduction of a
    specific published fire-danger index's coefficients).
    """

    #: ACF design choice (see normalizer.py's own disclosure) - not
    #: derived from an external published index's weighting. Weighted
    #: toward humidity/wind because low RH and strong wind are the
    #: physical drivers real published fire-danger indices
    #: consistently treat as dominant (fast fuel drying, fast spread
    #: rate) - the RELATIVE emphasis is informed by that consensus,
    #: the specific numbers are ACF's own.
    DEFAULT_WEIGHTS = {
        "humidity_dryness": 0.35,
        "wind": 0.25,
        "temperature": 0.20,
        "fuel_dryness": 0.20,
    }

    def __init__(self, weights: dict[str, float] | None = None) -> None:
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()
        total = sum(self.weights.values())
        if not (0.99 <= total <= 1.01):
            raise ValueError(f"Weights must sum to 1.0. Current sum: {total}")
        self.normalizer = FireWeatherNormalizer()

    def calculate_component_scores(self, data: dict[str, Any]) -> dict[str, float]:
        """
        Component scores in [0, 1] from `data`.

        Parameters
        ----------
        data : dict
            - temperature: degC (required)
            - relative_humidity: % (required)
            - wind_speed: m/s (required)
            - days_since_precipitation: days, optional. Defaults to
              0.0 - "no evidence of prolonged dryness supplied", not a
              fabricated confirmation that it rained recently; see
              this module's own honest disclosure.

        Raises
        ------
        KeyError
            If a required key is missing - forces the caller to supply
            real data rather than silently assuming a calm default for
            a safety-relevant index.
        """
        missing = [k for k in _REQUIRED_KEYS if k not in data]
        if missing:
            raise KeyError(f"FireWeatherCalculator requires {missing} - no calm-weather default is assumed")

        return {
            "humidity_dryness": self.normalizer.normalize_dryness_from_humidity(data["relative_humidity"]),
            "wind": self.normalizer.normalize_wind(data["wind_speed"]),
            "temperature": self.normalizer.normalize_temperature(data["temperature"]),
            "fuel_dryness": self.normalizer.normalize_days_since_precipitation(
                data.get("days_since_precipitation", 0.0)
            ),
        }

    def calculate(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Full Fire Weather Index result.

        Returns
        -------
        dict
            fire_weather_index : float (0-100)
            level : str, one of LOW/MODERATE/HIGH/VERY_HIGH/EXTREME
                (ACF-defined thresholds, see _LEVELS)
            decomposition : dict[str, float] - each component's
                contribution in index points, summing to
                fire_weather_index (up to rounding)
            component_scores : dict[str, float] - each component in
                [0, 100] before weighting
            explanation : list[str] - largest contributor first
        """
        scores = self.calculate_component_scores(data)

        decomposition = {}
        weighted_sum = 0.0
        for key, score in scores.items():
            weighted = score * self.weights[key]
            weighted_sum += weighted
            decomposition[key] = round(weighted * 100, 1)

        index = round(weighted_sum * 100, 1)
        level = self._get_level(index)

        return {
            "fire_weather_index": index,
            "level": level,
            "decomposition": decomposition,
            "component_scores": {k: round(v * 100, 1) for k, v in scores.items()},
            "explanation": self._explain(decomposition),
        }

    def _get_level(self, score: float) -> str:
        level = _LEVELS[0][1]
        for threshold, name in _LEVELS:
            if score >= threshold:
                level = name
        return level

    def _explain(self, decomposition: dict[str, float]) -> list[str]:
        labels = {
            "humidity_dryness": "Sécheresse (humidité relative)",
            "wind": "Vent",
            "temperature": "Température",
            "fuel_dryness": "Sécheresse prolongée (jours sans pluie)",
        }
        ranked = sorted(decomposition.items(), key=lambda kv: kv[1], reverse=True)
        explanation = []
        for key, points in ranked:
            if points < 0.5:
                continue
            explanation.append(f"{labels.get(key, key)} : {points} points sur 100")
        return explanation
