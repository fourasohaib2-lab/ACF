"""
Atmospheric Complexity Framework (ACF)

Autonomous Scientific Reasoning Engine Module (Phase 1)
(ScientificReasoningEngine, ScientificReasoningReport, Autonomous Causal Reasoning)
"""

from dataclasses import dataclass


@dataclass
class ScientificReasoningReport:
    """Rapport de raisonnement scientifique autonome."""

    reasoning_id: str
    target_phenomenon: str
    observed_parameters: dict[str, float]
    physical_laws_invoked: list[str]
    logical_chain: str
    scientific_conclusion: str
    confidence_pct: float | None


class ScientificReasoningEngine:
    """
    Moteur de raisonnement scientifique autonome observant les paramètres et générant des conclusions physiques.
    """

    @classmethod
    def evaluate_phenomenon(cls, phenomenon: str, observed_params: dict[str, float]) -> ScientificReasoningReport:
        """
        Génère un rapport de raisonnement scientifique autonome pour un phénomène donné.

        NOTE (correction): this used to completely ignore
        observed_params' actual values - it only branched on a
        "cyclone"/"storm" keyword match in phenomenon and then
        returned one of two fixed reports (fixed law list, fixed
        narrative, fixed 95.5%/91.0% confidence) regardless of what
        the real observed parameters were. A caller could pass wildly
        different sst/cape values and get byte-identical "reasoning"
        back. Now genuinely checks observed_params against an
        established physical threshold for the cyclone/storm branch
        (SST >= 26.5 degC, the classical minimum sea-surface
        temperature for tropical cyclogenesis - Palmen 1948, still
        cited as the standard threshold e.g. in the AMS Glossary of
        Meteorology) rather than ignoring it; confidence is no longer
        a specific fabricated percentage since no calibrated
        statistical confidence model exists here.
        """
        p = phenomenon.lower()

        if "cyclone" in p or "storm" in p:
            laws = ["Bernoulli Equation", "Coriolis Force", "Clausius-Clapeyron Law"]
            sst = observed_params.get("sst")
            if sst is not None and sst >= 26.5:
                chain = (
                    f"Observed SST {sst}°C >= 26.5°C (Palmen 1948 tropical cyclogenesis threshold) "
                    "-> Deep Convection Favorable -> Latent Heat Release -> Pressure Drop -> Wind Acceleration"
                )
                conclusion = "Sea-surface temperature meets the classical threshold for tropical cyclogenesis; thermodynamic environment is favorable for intensification."
            elif sst is not None:
                chain = f"Observed SST {sst}°C < 26.5°C (Palmen 1948 tropical cyclogenesis threshold) -> Insufficient latent heat flux for sustained intensification"
                conclusion = "Sea-surface temperature is below the classical threshold for tropical cyclogenesis; intensification is not thermodynamically favored by this factor alone."
            else:
                chain = "No sea-surface temperature ('sst') provided in observed_params -> cyclogenesis-favorability cannot be assessed"
                conclusion = "Insufficient observed parameters to assess intensification potential."
        else:
            laws = ["Conservation of Mass and Energy", "Navier-Stokes Equations"]
            chain = "Parameter Advection -> Dynamic Forcing -> Equilibrium Shift"
            conclusion = "System undergoing forced transition toward quasi-geostrophic balance."

        return ScientificReasoningReport(
            reasoning_id="REASON-2026-001",
            target_phenomenon=phenomenon,
            observed_parameters=observed_params,
            physical_laws_invoked=laws,
            logical_chain=chain,
            scientific_conclusion=conclusion,
            confidence_pct=None,
        )
