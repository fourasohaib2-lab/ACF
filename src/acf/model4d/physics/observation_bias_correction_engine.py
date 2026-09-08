"""
Atmospheric Complexity Framework (ACF)

MODEL4D - Observation Bias Correction Engine

Purpose:
--------
4D spatio-temporal grid mechanics, field representations, differential operators, and physical parameterizations.

Responsibilities:
-----------------
• Manage observation bias correction engine logic and state representations.
• Integrate with the model4d subsystem of the ACF scientific engine.

Major Components:
-----------------
• ObservationBiasCorrectionState, ObservationBiasCorrectionEngine

Dependencies:
-------------
• Python Standard Library and NumPy/Scientific Python Stack.
• Internal acf.model4d module infrastructure.

Scientific Context:
-------------------
Provides foundational capabilities for numerical weather prediction, atmospheric data processing,
physical modeling, and spatial-temporal analysis within the Atmospheric Complexity Framework.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ObservationBiasCorrectionState:
    satellite_bias: float
    radar_bias: float
    synop_bias: float
    metar_bias: float
    radiosonde_bias: float
    temperature: float
    humidity: float
    observation_quality: float


class ObservationBiasCorrectionEngine:
    """
    Atmospheric Complexity Framework
    Model4D

    Sprint 9.38
    Observation Bias Correction Engine
    """

    # ---------------------------------------------------------

    def satellite_bias_score(
        self,
        state: ObservationBiasCorrectionState,
    ) -> float:
        return round(state.satellite_bias * 0.90, 2)

    # ---------------------------------------------------------

    def radar_bias_score(
        self,
        state: ObservationBiasCorrectionState,
    ) -> float:
        return round(state.radar_bias * 0.88, 2)

    # ---------------------------------------------------------

    def synop_bias_score(
        self,
        state: ObservationBiasCorrectionState,
    ) -> float:
        return round(state.synop_bias * 0.91, 2)

    # ---------------------------------------------------------

    def metar_bias_score(
        self,
        state: ObservationBiasCorrectionState,
    ) -> float:
        return round(state.metar_bias * 0.89, 2)

    # ---------------------------------------------------------

    def radiosonde_bias_score(
        self,
        state: ObservationBiasCorrectionState,
    ) -> float:
        return round(state.radiosonde_bias * 0.93, 2)

    # ---------------------------------------------------------

    def temperature_bias(
        self,
        state: ObservationBiasCorrectionState,
    ) -> float:
        return round(abs(state.temperature - 288.0) / 10.0, 2)

    # ---------------------------------------------------------

    def humidity_bias(
        self,
        state: ObservationBiasCorrectionState,
    ) -> float:
        return round(abs(state.humidity - 50.0) / 20.0, 2)

    # ---------------------------------------------------------

    def systematic_bias(
        self,
        state: ObservationBiasCorrectionState,
    ) -> float:

        values = [
            self.satellite_bias_score(state),
            self.radar_bias_score(state),
            self.synop_bias_score(state),
            self.metar_bias_score(state),
            self.radiosonde_bias_score(state),
        ]

        return round(sum(values) / len(values), 2)

    # ---------------------------------------------------------

    def corrected_observation(
        self,
        state: ObservationBiasCorrectionState,
    ) -> float:

        return round(
            self.systematic_bias(state) - self.temperature_bias(state) - self.humidity_bias(state),
            2,
        )

    # ---------------------------------------------------------

    def bias_correction_update(
        self,
        state: ObservationBiasCorrectionState,
    ) -> dict:

        return {
            "satellite": self.satellite_bias_score(state),
            "radar": self.radar_bias_score(state),
            "synop": self.synop_bias_score(state),
            "metar": self.metar_bias_score(state),
            "radiosonde": self.radiosonde_bias_score(state),
            "temperature_bias": self.temperature_bias(state),
            "humidity_bias": self.humidity_bias(state),
            "systematic_bias": self.systematic_bias(state),
            "corrected_observation": self.corrected_observation(state),
            "bias_index": self.bias_index(state),
        }

    # ---------------------------------------------------------

    def bias_index(
        self,
        state: ObservationBiasCorrectionState,
    ) -> float:

        return round(
            self.corrected_observation(state) * state.observation_quality / 10.0,
            2,
        )
