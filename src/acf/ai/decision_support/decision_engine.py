"""
Atmospheric Complexity Framework (ACF)

AI-Assisted Operational Forecast Decision & Risk Assessment Engine
"""

from typing import Any

from acf.science.encyclopedia.knowledge_graph.graph_engine import KnowledgeGraphEngine
from acf.science.parameters.engine import ParameterEngine


class ForecastDecisionEngine:
    """
    Moteur de décision opérationnelle et d'évaluation des risques météorologiques majeurs.
    """

    def __init__(self):
        self.param_engine = ParameterEngine()
        self.graph = KnowledgeGraphEngine()

    def assess_severe_weather_risk(self, atmospheric_state: dict[str, float]) -> dict[str, Any]:
        """
        Évalue automatiquement le niveau de risque pour les phénomènes météorologiques violents
        et génère les recommandations opérationnelles assorties d'explications physiques.
        """
        cape = atmospheric_state.get("CAPE", 0.0)
        shear = atmospheric_state.get("shear_0_6km", 0.0)
        ehi = atmospheric_state.get("EHI", 0.0)
        ivt = atmospheric_state.get("IVT", 0.0)
        wind_gust = atmospheric_state.get("wind_gust_ms", 0.0)
        pwv = atmospheric_state.get("PWV", 0.0)

        risks = []
        warnings = []
        # NOTE (correction): confidence_score used to be a fixed 0.90
        # regardless of the input state - identical whether risk_level
        # came out "FAIBLE" (no thresholds crossed at all) or
        # "CRITIQUE / EXTRÊME" (every threshold crossed). This is a
        # deterministic rule-based threshold check, not a probabilistic/
        # ensemble forecast, so there is no real statistical basis here
        # to compute a genuine confidence number from (unlike
        # UncertaintyQuantificationEngine.decompose_uncertainty(), which
        # does have real ensemble variance to compute one from).
        # Honestly None instead, matching the same disclosure already
        # used by every other "no real basis for a confidence number"
        # engine in this package (emergency_assistant, digital_twin,
        # atmosphere_explorer, xai/explanation_generator).
        confidence = None

        # 1. Supercellules & Orages Violents
        if cape >= 1500.0 and shear >= 15.0:
            risks.append("Orages Supercellulaires / Grêle Forte")
            warnings.append("VIGILANCE ORAGES VIOLENTS : Fort potentiel de grêle (> 3 cm) et violentes rafales.")

        # 2. Risque de Tornade (EHI > 1.0)
        if ehi >= 1.0:
            risks.append("Risque Tornadique (Tornado Risk)")
            warnings.append("ALERTE TORNADE : Fort cisaillement et hélicité relative combinés à un CAPE élevé.")

        # 3. Ligne de Grain / Derecho
        if wind_gust >= 25.0:
            risks.append("Derecho / Vent Violemment Destructeur")
            warnings.append("VIGILANCE VENT FORT : Ligne de grain produisant des rafales descendantes macrorafales.")

        # 4. Rivière Atmosphérique / Pluie Diluvienne / Crue Éclair
        if ivt >= 500.0 or pwv >= 45.0:
            risks.append("Pluies Extrêmes / Rivière Atmosphérique / Crue Éclair")
            warnings.append("VIGILANCE CRUE ÉCLAIR : Transport de vapeur d'eau exceptionnel (IVT > 500 kg/m/s).")

        risk_level = "FAIBLE"
        if len(risks) == 1:
            risk_level = "MODÉRÉ"
        elif len(risks) == 2:
            risk_level = "ÉLEVÉ"
        elif len(risks) >= 3:
            risk_level = "CRITIQUE / EXTRÊME"

        explanation_text = (
            f"Évaluation du risque basée sur les paramètres d'état : CAPE = {cape:.0f} J/kg, "
            f"Cisaillement 0-6km = {shear:.1f} m/s, IVT = {ivt:.0f} kg/m/s. "
        )
        if risk_level != "FAIBLE":
            explanation_text += (
                "L'association d'une forte instabilité thermodynamique (Theta_e élevé) "
                "et d'un cisaillement dynamique profond favorise l'organisation méso-échelle des systèmes convectifs."
            )

        return {
            "risk_level": risk_level,
            "detected_phenomena": risks,
            "operational_warnings": warnings,
            "confidence_score": confidence,
            "physical_explanation": explanation_text,
            "reasoning_chain": "Surface Heating -> CAPE > 1500 -> Shear > 15m/s -> Organized Supercells",
            "equations_involved": [
                r"\text{CAPE} = \int_{z_{\text{LFC}}}^{z_{\text{EL}}} g \frac{T_v - T_{ve}}{T_{ve}} dz",
                r"\text{EHI} = \frac{\text{CAPE} \cdot \text{SREH}_{0-1\text{km}}}{160000}",
            ],
            "references": ["NOAA SPC Severe Weather Criteria", "Doswell et al. (1996) Weather and Forecasting"],
        }
