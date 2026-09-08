"""
Atmospheric Complexity Framework (ACF)

Forecast Explainability Engine

Sprint 9.30

This engine explains why a forecast or an AI decision has been produced.

It transforms numerical reasoning into understandable scientific and
operational explanations.

Author:
Atmospheric Complexity Framework

"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ForecastExplainabilityState:
    """
    Forecast explainability state.
    """

    hazard_index: float

    confidence: float

    decision: str

    causes: list[str] = field(default_factory=list)

    recommended_action: str = ""


class ForecastExplainabilityEngine:
    """
    Forecast Explainability Engine.

    Main goals

    - Explain AI forecast decisions.

    - Produce scientific explanation.

    - Produce operational explanation.

    - Produce human readable explanation.

    """

    # ==========================================================
    # Scientific explanation
    # ==========================================================

    def scientific_explanation(
        self,
        state: ForecastExplainabilityState,
    ) -> str:

        text = (
            f"The forecast decision '{state.decision}' "
            f"was generated from a hazard index of "
            f"{state.hazard_index:.2f} "
            f"with an estimated confidence of "
            f"{state.confidence:.2f}%."
        )

        if state.causes:
            text += " Main scientific causes: "

            text += ", ".join(state.causes)

            text += "."

        return text

    # ==========================================================
    # Human explanation
    # ==========================================================

    def human_explanation(
        self,
        state: ForecastExplainabilityState,
    ) -> str:

        if state.hazard_index >= 90:
            return "Very dangerous weather conditions are expected."

        if state.hazard_index >= 75:
            return "Hazardous weather conditions are expected."

        if state.hazard_index >= 50:
            return "Moderate weather instability is expected."

        return "No significant hazardous weather is expected."

    # ==========================================================
    # Confidence interpretation
    # ==========================================================

    def confidence_comment(
        self,
        state: ForecastExplainabilityState,
    ) -> str:

        if state.confidence >= 95:
            return "Forecast confidence is extremely high."

        if state.confidence >= 85:
            return "Forecast confidence is high."

        if state.confidence >= 70:
            return "Forecast confidence is moderate."

        return "Forecast confidence is low."

    # ==========================================================
    # Operational summary
    # ==========================================================

    def operational_summary(
        self,
        state: ForecastExplainabilityState,
    ) -> str:

        summary = (
            f"Decision: {state.decision}\nHazard Index: {state.hazard_index:.2f}\nConfidence: {state.confidence:.2f}%\n"
        )

        if state.recommended_action:
            summary += f"Recommended Action: {state.recommended_action}\n"

        if state.causes:
            summary += "Primary Causes:\n"

            for cause in state.causes:
                summary += f" - {cause}\n"

        return summary.strip()

    # ==========================================================
    # Complete explanation
    # ==========================================================

    def full_explanation(
        self,
        state: ForecastExplainabilityState,
    ) -> dict[str, object]:

        return {
            "decision": state.decision,
            "hazard_index": round(state.hazard_index, 2),
            "confidence": round(state.confidence, 2),
            "scientific": self.scientific_explanation(state),
            "human": self.human_explanation(state),
            "confidence_comment": self.confidence_comment(state),
            "summary": self.operational_summary(state),
            "recommended_action": state.recommended_action,
            "causes": list(state.causes),
        }

    # ==========================================================
    # Export
    # ==========================================================

    def export_report(
        self,
        state: ForecastExplainabilityState,
    ) -> str:

        report = []

        report.append("========== ACF Forecast Explainability ==========")

        report.append(self.operational_summary(state))

        report.append("")

        report.append("Scientific Explanation")

        report.append(self.scientific_explanation(state))

        report.append("")

        report.append("Human Explanation")

        report.append(self.human_explanation(state))

        report.append("")

        report.append(self.confidence_comment(state))

        return "\n".join(report)
