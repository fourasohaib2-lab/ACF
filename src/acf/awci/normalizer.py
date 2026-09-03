"""
AWCI Normalizer
===============

Normalizes variables to [0, 1] range for AWCI calculation.
"""

from acf.awci.scientific_status import ThresholdStatus, get_normalizer_range_status


class Normalizer:
    """
    Normalizes meteorological variables to [0, 1].

    Each variable has its own normalization function based on
    typical ranges.
    """

    @staticmethod
    def get_range_status(variable: str) -> ThresholdStatus:
        """
        Real scientific status of the range normalize_<variable>() uses
        (docs/ACF_MASTER_PROMPT.md section 79 - a threshold "n'est pas
        scientifiquement valide simplement parce qu'il est intuitif")
        - see acf.awci.scientific_status for the real classification.
        `variable` matches the normalize_*() method name's own suffix,
        e.g. "wind" for normalize_wind(), "cape" for normalize_cape().
        """
        return get_normalizer_range_status(variable)

    @staticmethod
    def normalize_temperature(value: float, is_kelvin: bool = True) -> float:
        """
        Normalize temperature to [0, 1].

        Range: -30°C to +50°C (243K to 323K)
        """
        if is_kelvin:
            T_c = value - 273.15
        else:
            T_c = value

        # Clip to range
        T_c = max(-30.0, min(50.0, T_c))

        # Normalize to [0, 1]
        return (T_c + 30.0) / 80.0

    @staticmethod
    def normalize_wind(value: float) -> float:
        """
        Normalize wind speed to [0, 1].

        Range: 0 to 50 m/s
        """
        value = max(0.0, min(50.0, value))
        return value / 50.0

    @staticmethod
    def normalize_wind_shear(value: float) -> float:
        """
        Normalize real bulk wind shear magnitude to [0, 1] - feeds the
        dynamic module alongside wind speed, when a caller supplies a
        real value (docs/ACF_MASTER_PROMPT.md section 12, explicit
        user request "commence par le module dynamique, avec le
        cisaillement de vent"; see
        acf.awci.wind_shear.compute_real_wind_shear_at_point() for the
        real formula that produces this input).

        Range: 0 to 50 m/s - the same envelope as normalize_wind()
        above, for internal consistency, generously wide relative to
        real operational significant-shear thresholds (e.g. ~20 m/s
        bulk shear is a commonly cited real operational threshold for
        organized severe convection potential) - not itself a
        classification boundary this function applies.
        """
        value = max(0.0, min(50.0, value))
        return value / 50.0

    @staticmethod
    def normalize_humidity(value: float) -> float:
        """
        Normalize specific humidity to [0, 1].

        Range: 0 to 0.03 kg/kg
        """
        value = max(0.0, min(0.03, value))
        return value / 0.03

    @staticmethod
    def normalize_cape(value: float) -> float:
        """
        Normalize CAPE to [0, 1].

        Range: 0 to 5000 J/kg
        """
        value = max(0.0, min(5000.0, value))
        return value / 5000.0

    @staticmethod
    def normalize_cin(value: float) -> float:
        """
        Normalize CIN to [0, 1].

        Range: 0 to -500 J/kg (negative values)
        """
        # CIN is negative, convert to positive for normalization
        value = abs(value)
        value = max(0.0, min(500.0, value))
        return value / 500.0

    @staticmethod
    def normalize_precipitation(value: float) -> float:
        """
        Normalize precipitation rate to [0, 1].

        Range: 0 to 50 mm/h
        """
        value = max(0.0, min(50.0, value))
        return value / 50.0

    @staticmethod
    def normalize_pressure(value: float) -> float:
        """
        Normalize pressure to [0, 1].

        Range: 800 to 1050 hPa
        """
        value = max(800.0, min(1050.0, value))
        return (value - 800.0) / 250.0

    @staticmethod
    def normalize_topographic(value: float, max_altitude: float = 3000.0) -> float:
        """
        Normalize topographic complexity to [0, 1].

        Range: 0 to max_altitude meters
        """
        value = max(0.0, min(max_altitude, value))
        return value / max_altitude

    @staticmethod
    def normalize_confidence(value: float) -> float:
        """
        Normalize confidence to [0, 1].

        Range: 0 to 100%
        """
        value = max(0.0, min(100.0, value))
        return value / 100.0

    @staticmethod
    def normalize_temporal(value: float, max_change: float = 20.0) -> float:
        """
        Normalize temporal evolution to [0, 1].

        Range: 0 to max_change units
        """
        value = max(0.0, min(max_change, value))
        return value / max_change

    @staticmethod
    def normalize_specific_humidity(value: float) -> float:
        """
        Normalize specific humidity to [0, 1].

        Range: 0 to 0.03 kg/kg
        """
        return Normalizer.normalize_humidity(value)

    # Reference "large disagreement" spread per variable, used to
    # normalize a real ensemble standard deviation (from
    # acf.ai.ensemble.ensemble_manager.EnsembleManager.spread) to
    # [0, 1]. Like AWCICalculator.INTERACTION_WEIGHTS, these are an ACF
    # design choice (no published external standard defines "large" CAPE
    # ensemble spread for this composite index) - documented as such,
    # not presented as a literature result. A spread at or above the
    # reference saturates to 1.0 (maximum forecast complexity from that
    # variable), not an error.
    ENSEMBLE_SPREAD_REFERENCE = {
        "cape": 1500.0,  # J/kg - members disagreeing by this much on CAPE is a very unsettled convective forecast
        "wind_speed": 15.0,  # m/s
        "temperature": 5.0,  # K
        "precipitation": 20.0,  # mm/h
    }

    # Reference "large disagreement" spread for real multi-model
    # comparisons (acf.visualization.ai_forecast_center.
    # model_consensus_engine.ModelConsensusEngine.
    # compute_real_multi_model_disagreement()), analogous to
    # ENSEMBLE_SPREAD_REFERENCE above but a conceptually distinct
    # signal: spread ACROSS different model grid configurations, not
    # across perturbed members of one model. Kept as its own dict (not
    # merged with ENSEMBLE_SPREAD_REFERENCE) so the two stay separately
    # tunable - real inter-model disagreement and real ensemble spread
    # are not guaranteed to have the same typical magnitude. Currently
    # only "temperature" is populated - the only field
    # compute_real_multi_model_disagreement() has been exercised with
    # so far (see that method's `field` parameter to extend).
    MODEL_DISAGREEMENT_REFERENCE = {
        "temperature": 5.0,  # K - see model_consensus_engine.py's own measured magnitudes
    }

    @staticmethod
    def _normalize_spread(spread: float, reference: float) -> float:
        """Shared clamp-and-scale logic for normalize_ensemble_spread() and normalize_model_disagreement()."""
        spread = max(0.0, spread)
        return min(1.0, spread / reference)

    @staticmethod
    def normalize_ensemble_spread(spread: float, variable: str) -> float:
        """
        Normalize a real ensemble spread (standard deviation across
        forecast members, e.g. from EnsembleManager.spread) to [0, 1].

        Parameters
        ----------
        spread : float
            Standard deviation across ensemble members, in the
            variable's native units. Always >= 0 by construction
            (it's a standard deviation) - a negative value is a
            caller bug, not a valid "low disagreement" signal, and is
            clamped to 0 rather than silently accepted.
        variable : str
            One of ENSEMBLE_SPREAD_REFERENCE's keys.

        Returns
        -------
        float
            spread / reference, clamped to [0, 1].

        Raises
        ------
        KeyError
            If `variable` has no declared reference spread - silently
            falling back to some default would fabricate a
            normalization scale nobody chose.
        """
        return Normalizer._normalize_spread(spread, Normalizer.ENSEMBLE_SPREAD_REFERENCE[variable])

    @staticmethod
    def normalize_model_disagreement(spread: float, variable: str) -> float:
        """
        Normalize a real multi-model disagreement spread (standard
        deviation across models' real point values, e.g. from
        ModelConsensusEngine.compute_real_multi_model_disagreement()'s
        disagreement_spread) to [0, 1]. Same mechanics as
        normalize_ensemble_spread() (see _normalize_spread()), against
        the separate MODEL_DISAGREEMENT_REFERENCE scale.

        Raises
        ------
        KeyError
            If `variable` has no declared reference spread.
        """
        return Normalizer._normalize_spread(spread, Normalizer.MODEL_DISAGREEMENT_REFERENCE[variable])

    @staticmethod
    def normalize_percentile(value: float, climatology: list[float]) -> float:
        """
        Normalize a value to [0, 1] using its empirical percentile rank
        within a climatological reference sample, instead of a fixed
        min-max range.

        This is more robust than the fixed-range normalize_*() methods
        above for a station/sector whose typical value range differs
        from the generic assumptions hard-coded there (e.g. a very
        windy coastal station vs. a sheltered inland one) — the same
        raw value can represent very different relative complexity
        depending on local climatology.

        Parameters
        ----------
        value : float
            The value to normalize.
        climatology : list of float
            A reference sample of historical values for the same
            variable, station and (ideally) season. Not required to be
            pre-sorted.

        Returns
        -------
        float
            Empirical percentile rank in [0, 1] (fraction of the
            climatological sample at or below `value`). Returns 0.5
            (neutral) if the climatology sample is empty.
        """
        if not climatology:
            return 0.5

        sorted_clim = sorted(climatology)
        n = len(sorted_clim)

        # Count of climatology values <= value (linear scan is fine —
        # climatology samples for this use case are typically small,
        # e.g. a season's worth of station observations).
        count_at_or_below = sum(1 for c in sorted_clim if c <= value)

        return count_at_or_below / n
