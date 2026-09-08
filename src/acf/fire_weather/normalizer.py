"""
Normalization ranges for FireWeatherCalculator's inputs.

Same disclosure convention as acf.awci.normalizer.Normalizer: these
ranges are an ACF design choice (informed by which physical quantities
real published fire-danger indices use, not a reproduction of any of
their specific numeric formulas - see fire_weather/__init__.py's own
docstring), not derived from an external published source.
"""


class FireWeatherNormalizer:
    @staticmethod
    def normalize_temperature(temp_c: float) -> float:
        """
        Higher temperature -> faster fuel drying / lower ignition
        threshold -> higher contribution. Range: 0 to 45 degC.
        """
        temp_c = max(0.0, min(45.0, temp_c))
        return temp_c / 45.0

    @staticmethod
    def normalize_dryness_from_humidity(relative_humidity_pct: float) -> float:
        """
        LOWER relative humidity -> drier fuel -> HIGHER contribution
        (inverse relationship - real, uncontroversial physics: dead
        fuel moisture tracks ambient RH). Range: 0-100%.
        """
        rh = max(0.0, min(100.0, relative_humidity_pct))
        return (100.0 - rh) / 100.0

    @staticmethod
    def normalize_wind(wind_speed_m_s: float) -> float:
        """
        Higher wind -> faster fire spread rate and more oxygen supply
        to the flame front -> higher contribution. Range: 0-20 m/s.
        """
        wind = max(0.0, min(20.0, wind_speed_m_s))
        return wind / 20.0

    @staticmethod
    def normalize_days_since_precipitation(days: float) -> float:
        """
        More days since meaningful precipitation -> drier fuel ->
        higher contribution. Range: 0-21 days (three weeks).
        """
        days = max(0.0, min(21.0, days))
        return days / 21.0
