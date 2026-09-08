"""
Atmospheric Complexity Framework (ACF)

Cosmic Hazard & Extraterrestrial Risk Engine Module (Phase 10)
(CosmicHazardEngine, CosmicRiskLevel, ThreatAssessment for Asteroid Impact, Solar Storm, GRB, Supernovae, Cosmic Rays)

NOTE (correction — fabricated threat assessment, found during the
post-model4d audit, 2026-09-05): evaluate_threats() used to
unconditionally return a fixed list of exactly 3 threats (generic
asteroid, solar storm, GRB) with specific-looking
probability_per_century numbers (0.01, 0.12, 0.00001) and invented
"HAZ-..." IDs, with zero real NEO catalog or astronomical-monitoring
feed connected - identical on every call, not derived from any real
data. Same fabrication family already found and fixed in this same
package's planetary_ai.py (PlanetaryReasoningEngine.
run_planetary_reasoning_chain() used to return a fixed narrative for
any object_name) - this sibling file was missed by that pass.

Fix, matching planetary_ai.py's own convention (derive from a real
registry, disclose rather than invent what can't be computed): the
asteroid entry now genuinely derives from PlanetaryDefenseRegistry /
PlanetaryDatabase's HAZARD_ASSESSMENT_REGISTRY. Bennu is the only NEO
in this module with both a real orbital entry and a vetted Torino/
Palermo hazard assessment - NEO_REGISTRY's own Apophis entry documents
impact_probability=0.0 ("Éliminé pour 2029/2036/2068") and Chicxulub
already impacted 66 Ma ago, so neither is a live future risk to
report here. Solar Storm, Gamma Ray Burst, and Cosmic Ray hazard TYPES
are kept (real, well-documented categories in the planetary-defense/
heliophysics literature) but their probability_per_century and
risk_level are now honestly unassessed - no real space-weather or
astronomical-survey feed is connected in this module to compute one
(acf.space_weather has its own separate, real forecast engines for
solar/geomagnetic hazards - not wired up here; a real integration
would import from there rather than inventing a number in this file).
"""

from dataclasses import dataclass

from acf.planetary.planetary_database import PlanetaryDatabase, PlanetaryDefenseRegistry


@dataclass
class ThreatAssessment:
    """Bilan d'évaluation des menaces cosmiques."""

    hazard_id: str
    hazard_type: str  # Asteroid Impact, Solar Storm, Gamma Ray Burst, Supernova, Cosmic Rays
    risk_level: str  # NONE, LOW, MEDIUM, HIGH, CRITICAL, CATACLYSMIC, or UNASSESSED
    probability_per_century: float | None  # None when no real monitoring feed backs a number
    mitigation_strategy: str
    is_real_data: bool


class CosmicRiskLevel:
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    CATACLYSMIC = "CATACLYSMIC"
    UNASSESSED = "UNASSESSED_NO_REAL_MONITORING_CONNECTED"


class CosmicHazardEngine:
    """
    Moteur de détection et d'évaluation des risques et menaces cosmiques globales.
    """

    @classmethod
    def evaluate_threats(cls) -> list[ThreatAssessment]:
        """Évalue les menaces cosmiques pesant sur le système Terre."""
        threats: list[ThreatAssessment] = []

        bennu = PlanetaryDefenseRegistry.get_neo("bennu")
        bennu_hazard = PlanetaryDatabase.get_sample_hazard("bennu")
        if bennu is not None and bennu_hazard is not None:
            # Torino Scale 1 (real, sourced from HAZARD_ASSESSMENT_REGISTRY)
            # is IAU-defined as a routine discovery meriting careful
            # monitoring, not an unusual level of danger - LOW is the
            # honest mapping, not an invented HIGH/MEDIUM.
            threats.append(
                ThreatAssessment(
                    hazard_id=f"NEO-{bennu.neo_id}",
                    hazard_type=f"Near-Earth Asteroid Impact ({bennu.name})",
                    risk_level=CosmicRiskLevel.LOW,
                    probability_per_century=bennu.impact_probability,
                    mitigation_strategy="Kinetic Impactor (DART Type) or Nuclear Deflection Mission",
                    is_real_data=True,
                )
            )

        threats.append(
            ThreatAssessment(
                hazard_id="HAZ-SOLAR-GENERIC",
                hazard_type="Extreme Solar Proton Event / Carrington-Class Event",
                risk_level=CosmicRiskLevel.UNASSESSED,
                probability_per_century=None,
                mitigation_strategy="Power Grid Hardening & Satellite Safe-Mode Shutdown",
                is_real_data=False,
            )
        )
        threats.append(
            ThreatAssessment(
                hazard_id="HAZ-GRB-GENERIC",
                hazard_type="Nearby Gamma Ray Burst (< 6000 light-years)",
                risk_level=CosmicRiskLevel.UNASSESSED,
                probability_per_century=None,
                mitigation_strategy="Ozone Depletion Protection & Atmospheric Monitoring",
                is_real_data=False,
            )
        )

        return threats
