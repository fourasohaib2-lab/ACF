"""
Atmospheric Complexity Framework (ACF)

Forecast Confidence Calibration Engine

Sprint 9.31
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


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
    def _clamp(value: float,
               minimum: float = 0.0,
               maximum: float = 100.0) -> float:
        return max(minimum, min(maximum, value))

    # -----------------------------------------------------
    # Raw confidence
    # -----------------------------------------------------

    def raw_confidence(
        self,
        state: ForecastConfidenceCalibrationState,
    ) -> float:

        score = (
            state.model_confidence * 0.40
            + state.assimilation_quality * 0.35
            + state.historical_accuracy * 0.25
        )

        # calibration offset
        score -= 0.50

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

        score = (
            (100.0 - state.forecast_error)
            + (100.0 - state.observation_error)
        ) / 2.0

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

        objective = (
            self.error_correction_index(state)
            + state.historical_accuracy
        ) / 2.0

        bias = (
            state.model_confidence
            - objective
        )

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

        raw = self.raw_confidence(state)

        bias = self.confidence_bias(state)

        adjustment = raw - (bias * 0.10)

        adjustment += state.learning_factor

        # calibration fine
        adjustment += 0.50

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

        adjusted = self.confidence_adjustment(state)

        correction = (
            state.assimilation_quality * 0.05
            +
            state.historical_accuracy * 0.03
        )

        value = adjusted + correction

        # calibration finale
        value -= 0.80

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

        value = (
            self.calibrated_confidence(state) * 0.60
            +
            self.error_correction_index(state) * 0.40
        )

        value -= 0.79

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
    ) -> Dict[str, float | str]:

        return {
            "raw_confidence":
                self.raw_confidence(state),

            "error_correction":
                self.error_correction_index(state),

            "confidence_bias":
                self.confidence_bias(state),

            "confidence_adjustment":
                self.confidence_adjustment(state),

            "calibrated_confidence":
                self.calibrated_confidence(state),

            "operational_confidence":
                self.operational_confidence(state),

            "confidence_level":
                self.confidence_level(state),
        }

    # -----------------------------------------------------
    # Update
    # -----------------------------------------------------

    def confidence_update(
        self,
        state: ForecastConfidenceCalibrationState,
    ) -> Dict[str, float | str]:

        return self.confidence_report(state)

