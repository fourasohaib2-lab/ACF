"""
Climatology
============

Percentile-based climatological anomalies, z-scores, and heat/cold
wave detection following the ETCCDI Warm/Cold Spell Duration Index
(WSDI/CSDI) convention.

NOTE on duration: the plan referenced "5 jours" for heat/cold wave
duration, but the standard ETCCDI WSDI/CSDI definition (verified via
WebSearch) actually specifies >= 6 CONSECUTIVE days above/below the
90th/10th percentile (the percentile threshold itself is computed
using a 5-day window — a different "5" from the wave duration, likely
the source of the mix-up). ACF follows the verified ETCCDI standard
(6 days) as the default, exposed as a parameter rather than hard-coded,
since several national services do use other day-counts operationally.

Reference:
    ETCCDI (Expert Team on Climate Change Detection and Indices) —
    WSDI: "annual count of days with at least 6 consecutive days when
    TX > 90th percentile" (90th percentile computed over a 5-day
    window of the base period).
"""

from dataclasses import dataclass, field


@dataclass
class ClimatologicalRecord:
    """A historical sample of values for one variable/station/calendar-window."""

    variable: str
    station_id: str
    values: list[float] = field(default_factory=list)

    def percentile_value(self, percentile: float) -> float:
        """Convenience: Climatology.percentile_value(self.values, percentile)."""
        return Climatology.percentile_value(self.values, percentile)

    def z_score(self, value: float) -> float:
        """Convenience: Climatology.z_score(value, self.values)."""
        return Climatology.z_score(value, self.values)


class Climatology:
    """Percentile, z-score, and standardized anomaly calculations."""

    @staticmethod
    def percentile_value(historical_sample: list[float], percentile: float) -> float:
        """
        Value at a given percentile of a historical sample, via linear
        interpolation between order statistics (the standard "linear"
        method, matching numpy.percentile's default).

        Parameters
        ----------
        historical_sample : list of float
            Historical values, non-empty.
        percentile : float
            Percentile in [0, 100].

        Returns
        -------
        float
            The interpolated value at that percentile.

        Raises
        ------
        ValueError
            If historical_sample is empty or percentile is out of [0, 100].
        """
        if not historical_sample:
            raise ValueError("historical_sample must not be empty.")
        if not (0.0 <= percentile <= 100.0):
            raise ValueError("percentile must be in [0, 100].")

        sorted_sample = sorted(historical_sample)
        n = len(sorted_sample)
        if n == 1:
            return sorted_sample[0]

        rank = (percentile / 100.0) * (n - 1)
        lower_idx = int(rank)
        upper_idx = min(lower_idx + 1, n - 1)
        frac = rank - lower_idx

        return sorted_sample[lower_idx] + frac * (sorted_sample[upper_idx] - sorted_sample[lower_idx])

    @staticmethod
    def z_score(value: float, historical_sample: list[float]) -> float:
        """
        Standardized anomaly: z = (value - mean) / stddev (population
        standard deviation).

        Parameters
        ----------
        value : float
            The value to standardize.
        historical_sample : list of float
            Historical reference sample, at least 2 values (stddev
            needs variance).

        Returns
        -------
        float
            z-score (dimensionless).

        Raises
        ------
        ValueError
            If historical_sample has fewer than 2 values or zero
            variance (stddev = 0, division undefined).
        """
        n = len(historical_sample)
        if n < 2:
            raise ValueError("historical_sample must have at least 2 values.")

        mean = sum(historical_sample) / n
        variance = sum((x - mean) ** 2 for x in historical_sample) / n
        stddev = variance**0.5

        if stddev == 0:
            raise ValueError("historical_sample has zero variance; z-score is undefined.")

        return (value - mean) / stddev


class HeatColdWave:
    """ETCCDI-style Warm/Cold Spell Duration detection."""

    DEFAULT_MIN_CONSECUTIVE_DAYS = 6  # ETCCDI WSDI/CSDI standard, verified.
    WARM_PERCENTILE = 90.0
    COLD_PERCENTILE = 10.0

    @staticmethod
    def detect_spells(
        daily_values: list[float],
        threshold: float,
        above_threshold: bool,
        min_consecutive_days: int = DEFAULT_MIN_CONSECUTIVE_DAYS,
    ) -> list[tuple[int, int]]:
        """
        Find runs of >= min_consecutive_days consecutive days where
        daily_values[i] is above (or below) threshold.

        Parameters
        ----------
        daily_values : list of float
            Daily values in chronological order (e.g. daily Tmax for a
            warm spell, daily Tmin for a cold spell).
        threshold : float
            The percentile-derived threshold (e.g. from
            Climatology.percentile_value(..., 90) for a warm spell).
        above_threshold : bool
            True to find spells where value > threshold (warm spell,
            WSDI-style); False for value < threshold (cold spell,
            CSDI-style).
        min_consecutive_days : int
            Minimum run length to count as a spell. Defaults to the
            verified ETCCDI standard of 6.

        Returns
        -------
        list of (start_index, end_index) tuples (inclusive, 0-based)
            for each qualifying spell.
        """
        if min_consecutive_days < 1:
            raise ValueError("min_consecutive_days must be at least 1.")

        spells = []
        run_start = None

        for i, value in enumerate(daily_values):
            exceeds = value > threshold if above_threshold else value < threshold
            if exceeds:
                if run_start is None:
                    run_start = i
            else:
                if run_start is not None and (i - run_start) >= min_consecutive_days:
                    spells.append((run_start, i - 1))
                run_start = None

        # Handle a run extending to the end of the series.
        if run_start is not None and (len(daily_values) - run_start) >= min_consecutive_days:
            spells.append((run_start, len(daily_values) - 1))

        return spells

    @staticmethod
    def wsdi_day_count(
        daily_tmax: list[float],
        climatological_tmax_sample: list[float],
        min_consecutive_days: int = DEFAULT_MIN_CONSECUTIVE_DAYS,
    ) -> int:
        """
        Warm Spell Duration Index: total number of days that fall
        within qualifying warm spells (>= min_consecutive_days
        consecutive days with Tmax > 90th percentile).

        Parameters
        ----------
        daily_tmax : list of float
            Daily maximum temperature series in chronological order.
        climatological_tmax_sample : list of float
            Historical Tmax sample used to derive the 90th percentile
            threshold.
        min_consecutive_days : int
            Defaults to the ETCCDI standard of 6.

        Returns
        -------
        int
            Total day-count within qualifying warm spells (WSDI).

        Reference
        ---------
        ETCCDI WSDI definition (verified).
        """
        threshold = Climatology.percentile_value(climatological_tmax_sample, HeatColdWave.WARM_PERCENTILE)
        spells = HeatColdWave.detect_spells(daily_tmax, threshold, above_threshold=True, min_consecutive_days=min_consecutive_days)
        return sum(end - start + 1 for start, end in spells)

    @staticmethod
    def csdi_day_count(
        daily_tmin: list[float],
        climatological_tmin_sample: list[float],
        min_consecutive_days: int = DEFAULT_MIN_CONSECUTIVE_DAYS,
    ) -> int:
        """
        Cold Spell Duration Index: total number of days that fall
        within qualifying cold spells (>= min_consecutive_days
        consecutive days with Tmin < 10th percentile). Mirror of
        wsdi_day_count().
        """
        threshold = Climatology.percentile_value(climatological_tmin_sample, HeatColdWave.COLD_PERCENTILE)
        spells = HeatColdWave.detect_spells(daily_tmin, threshold, above_threshold=False, min_consecutive_days=min_consecutive_days)
        return sum(end - start + 1 for start, end in spells)
