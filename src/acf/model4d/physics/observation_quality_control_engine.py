from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ObservationQualityControlState:
    synop_quality: float
    metar_quality: float
    radiosonde_quality: float
    radar_quality: float
    satellite_quality: float
    temporal_consistency: float
    spatial_consistency: float
    observation_quality: float
    temperature: float
    humidity: float


class ObservationQualityControlEngine:
    """
    Model4D Observation Quality Control Engine

    Sprint 9.37
    """

    def synop_quality_score(
        self,
        state: ObservationQualityControlState,
    ) -> float:
        return round(state.synop_quality * 0.90, 2)

    def metar_quality_score(
        self,
        state: ObservationQualityControlState,
    ) -> float:
        return round(state.metar_quality * 0.88, 2)

    def radiosonde_quality_score(
        self,
        state: ObservationQualityControlState,
    ) -> float:
        return round(state.radiosonde_quality * 0.92, 2)

    def radar_quality_score(
        self,
        state: ObservationQualityControlState,
    ) -> float:
        return round(state.radar_quality * 0.91, 2)

    def satellite_quality_score(
        self,
        state: ObservationQualityControlState,
    ) -> float:
        return round(state.satellite_quality * 0.89, 2)

    def temporal_consistency(
        self,
        state: ObservationQualityControlState,
    ) -> float:
        return round(state.temporal_consistency * 0.95, 2)

    def spatial_consistency(
        self,
        state: ObservationQualityControlState,
    ) -> float:
        return round(state.spatial_consistency * 0.95, 2)

    def observation_reliability(
        self,
        state: ObservationQualityControlState,
    ) -> float:

        values = [
            self.synop_quality_score(state),
            self.metar_quality_score(state),
            self.radiosonde_quality_score(state),
            self.radar_quality_score(state),
            self.satellite_quality_score(state),
            self.temporal_consistency(state),
            self.spatial_consistency(state),
        ]

        return round(sum(values) / len(values), 2)

    def outlier_detection(
        self,
        state: ObservationQualityControlState,
    ) -> bool:

        if state.temperature < 150:
            return True

        if state.temperature > 340:
            return True

        if state.humidity < 0:
            return True

        if state.humidity > 100:
            return True

        return False

    def quality_control_update(
        self,
        state: ObservationQualityControlState,
    ) -> dict:

        return {
            "synop": self.synop_quality_score(state),
            "metar": self.metar_quality_score(state),
            "radiosonde": self.radiosonde_quality_score(state),
            "radar": self.radar_quality_score(state),
            "satellite": self.satellite_quality_score(state),
            "temporal": self.temporal_consistency(state),
            "spatial": self.spatial_consistency(state),
            "reliability": self.observation_reliability(state),
            "outlier": self.outlier_detection(state),
            "quality_index": self.quality_index(state),
        }

    def quality_index(
        self,
        state: ObservationQualityControlState,
    ) -> float:

        return round(
            self.observation_reliability(state)
            * state.observation_quality
            / 100.0,
            2,
        )
