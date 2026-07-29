from dataclasses import dataclass


@dataclass(slots=True)
class SelfImprovingForecastState:
    model_name: str
    initial_accuracy: float
    forecast_error: float
    learning_rate: float
    training_cycles: int
    neural_confidence: float


class SelfImprovingForecastNeuralEngine:
    """
    Atmospheric Complexity Framework

    Sprint 9.52
    Self Improving Forecast Neural Engine

    Adaptive AI learning layer for Model4D.
    """

    def improvement_gain(
        self,
        state: SelfImprovingForecastState,
    ) -> float:
        """
        Calculate learning improvement gain.
        """

        gain = (
            state.learning_rate
            * state.training_cycles
        )

        return round(
            gain,
            2,
        )


    def corrected_accuracy(
        self,
        state: SelfImprovingForecastState,
    ) -> float:
        """
        Improve forecast accuracy after learning.
        """

        accuracy = (
            state.initial_accuracy
            + self.improvement_gain(state)
            - state.forecast_error * 0.2
        )

        return round(
            max(min(accuracy, 100), 0),
            2,
        )


    def neural_learning_score(
        self,
        state: SelfImprovingForecastState,
    ) -> float:
        """
        Global neural learning performance.
        """

        score = (
            self.corrected_accuracy(state)
            + state.neural_confidence
        ) / 2

        return round(
            score,
            2,
        )


    def optimization_status(
        self,
        state: SelfImprovingForecastState,
    ) -> str:
        """
        Determine AI learning state.
        """

        score = self.neural_learning_score(state)

        if score >= 90:
            return "OPTIMAL_LEARNING"

        if score >= 70:
            return "ACTIVE_LEARNING"

        return "RETRAIN_REQUIRED"


    def learning_update(
        self,
        state: SelfImprovingForecastState,
    ) -> dict:
        """
        Generate neural learning update.
        """

        return {
            "model": state.model_name,
            "improvement_gain":
                self.improvement_gain(state),
            "corrected_accuracy":
                self.corrected_accuracy(state),
            "learning_score":
                self.neural_learning_score(state),
            "status":
                self.optimization_status(state),
        }
