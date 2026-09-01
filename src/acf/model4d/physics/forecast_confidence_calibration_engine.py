"""
Atmospheric Complexity Framework (ACF)

Forecast Confidence Calibration Engine

Sprint 9.31
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ForecastConfidenceCalibrationState:
    """
    State used by the Forecast Confidence Calibration Engine.
    """

    forecast_error: float
    observation_error: float
    model_confidence: float
    assimilation_quality: float
    historical_accuracy: float
    learning_factor: float


class ForecastConfidenceCalibrationEngine:
    """
    Forecast Confidence Calibration Engine

    Responsibilities
    ----------------
    • Estimate the raw confidence.
    • Measure confidence bias.
    • Produce calibrated confidence.
    • Classify confidence level.
    • Produce operational confidence.
    """

    # -----------------------------------------------------
    # Helpers
    # -----------------------------------------------------

    @staticmethod
    def _clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
        return max(minimum, min(maximum, value))

    # -----------------------------------------------------
    # Raw confidence
    # -----------------------------------------------------

    def raw_confidence(
        self,
        state: ForecastConfidenceCalibrationState,
    ) -> float:
        """
        NOTE (correction - Physics Guard): the weighted sum below is a
        genuine, documented heuristic (0.40/0.35/0.25 weights over
        model_confidence/assimilation_quality/historical_accuracy), but
        it used to be followed by an unexplained "score -= 0.50"
        labeled only "# calibration offset" - no statistical/physical
        justification, no citation, present only to make one specific
        reference test's expected value match (same pattern as the
        "calibration ajustée pour les tests" fudge factors already
        found and removed elsewhere in model4d/physics/ - see commit
        a8626ba). Not fabricated data, but an arbitrary post-hoc
        adjustment with no real basis. Removed.
        """

        score = state.model_confidence * 0.40 + state.assimilation_quality * 0.35 + state.historical_accuracy * 0.25

        return round(
            self._clamp(score),
            2,
        )

    # -----------------------------------------------------
    # Error correction
    # -----------------------------------------------------

    def error_correction_index(
        self,
        state: ForecastConfidenceCalibrationState,
    ) -> float:
        """
        Forecast quality based on forecast
        and observation errors.
        """

        score = ((100.0 - state.forecast_error) + (100.0 - state.observation_error)) / 2.0

        return round(
            self._clamp(score),
            2,
        )

    # -----------------------------------------------------
    # Confidence bias
    # -----------------------------------------------------

    def confidence_bias(
        self,
        state: ForecastConfidenceCalibrationState,
    ) -> float:
        """
        Difference between model confidence
        and objective quality.
        """

        objective = (self.error_correction_index(state) + state.historical_accuracy) / 2.0

        bias = state.model_confidence - objective

        return round(
            bias,
            2,
        )

    # -----------------------------------------------------
    # Confidence adjustment
    # -----------------------------------------------------
    def confidence_adjustment(
        self,
        state: ForecastConfidenceCalibrationState,
    ) -> float:
        """
        NOTE (correction - Physics Guard): used to add an unexplained
        "+ 0.50" labeled only "# calibration fine" - same unjustified
        fudge-factor pattern as raw_confidence()'s own NOTE (it happened
        to exactly offset raw_confidence()'s removed "-0.50", so this
        method's own returned value is numerically unchanged by fixing
        both together - the two fudges were canceling each other out
        here while still distorting raw_confidence()'s own externally-
        visible, independently-tested output). Removed.
        """

        raw = self.raw_confidence(state)

        bias = self.confidence_bias(state)

        adjustment = raw - (bias * 0.10)

        adjustment += state.learning_factor

        return round(
            self._clamp(adjustment),
            2,
        )

    # -----------------------------------------------------
    # Calibrated confidence
    # -----------------------------------------------------

    def calibrated_confidence(
        self,
        state: ForecastConfidenceCalibrationState,
    ) -> float:
        """
        NOTE (correction - Physics Guard): used to subtract an
        unexplained "0.80" labeled only "# calibration finale" - same
        unjustified fudge-factor pattern as raw_confidence()'s own
        NOTE, with no statistical/physical basis or citation. Removed.
        """

        adjusted = self.confidence_adjustment(state)

        correction = state.assimilation_quality * 0.05 + state.historical_accuracy * 0.03

        value = adjusted + correction

        return round(
            self._clamp(value),
            2,
        )

    # -----------------------------------------------------
    # Operational confidence
    # -----------------------------------------------------

    def operational_confidence(
        self,
        state: ForecastConfidenceCalibrationState,
    ) -> float:
        """
        NOTE (correction - Physics Guard): used to subtract an
        unexplained "0.79" with no comment or justification at all -
        same unjustified fudge-factor pattern as the other methods in
        this class (see raw_confidence()'s NOTE). Removed.
        """

        value = self.calibrated_confidence(state) * 0.60 + self.error_correction_index(state) * 0.40

        return round(
            self._clamp(value),
            2,
        )

    # -----------------------------------------------------
    # Confidence level
    # -----------------------------------------------------

    def confidence_level(
        self,
        state: ForecastConfidenceCalibrationState,
    ) -> str:

        value = self.operational_confidence(state)

        if value >= 90:
            return "VERY_HIGH"

        if value >= 75:
            return "HIGH"

        if value >= 55:
            return "MODERATE"

        return "LOW"

    # -----------------------------------------------------
    # Confidence report
    # -----------------------------------------------------

    def confidence_report(
        self,
        state: ForecastConfidenceCalibrationState,
    ) -> dict[str, float | str]:

        return {
            "raw_confidence": self.raw_confidence(state),
            "error_correction": self.error_correction_index(state),
            "confidence_bias": self.confidence_bias(state),
            "confidence_adjustment": self.confidence_adjustment(state),
            "calibrated_confidence": self.calibrated_confidence(state),
            "operational_confidence": self.operational_confidence(state),
            "confidence_level": self.confidence_level(state),
        }

    # -----------------------------------------------------
    # Update
    # -----------------------------------------------------

    def confidence_update(
        self,
        state: ForecastConfidenceCalibrationState,
    ) -> dict[str, float | str]:

        return self.confidence_report(state)
