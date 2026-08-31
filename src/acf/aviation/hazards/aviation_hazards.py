"""
Atmospheric Complexity Framework (ACF)

Global Aviation Meteorological Hazards Engine Module
(CAT, Mountain Waves, Wind Shear, Airframe Icing, Volcanic Ash, Microburst, Tropopause Folds)
"""

from dataclasses import dataclass


@dataclass
class AviationHazardInfo:
    """Description scientifique complète d'un danger météorologique pour l'aviation."""

    key: str
    name: str
    category: str  # "TURBULENCE", "ICING", "CONVECTION", "VISIBILITY", "VOLCANIC"
    physical_explanation: str
    governing_equation: str
    icao_thresholds: dict[str, str]
    operational_impacts: list[str]
    flight_recommendations: list[str]
    references: list[str]


AVIATION_HAZARDS_REGISTRY: dict[str, AviationHazardInfo] = {
    "cat_turbulence": AviationHazardInfo(
        key="cat_turbulence",
        name="Clear Air Turbulence (CAT - Turbulence en Air Clair)",
        category="TURBULENCE",
        physical_explanation=(
            "La turbulence en air clair se produit dans la haute troposphère/basse stratosphère (FL240-FL400) "
            "en dehors de toute convection visible, générée par l'instabilité de Kelvin-Helmholtz aux abords des cœurs de Jet Stream "
            "lorsque le nombre de Richardson chute sous la valeur critique Ri < 0.25."
        ),
        governing_equation=r"Ri = \frac{\frac{g}{\theta} \frac{\partial \theta}{\partial z}}{\left(\frac{\partial u}{\partial z}\right)^2 + \left(\frac{\partial v}{\partial z}\right)^2} < 0.25",
        icao_thresholds={
            "MODERATE_CAT": "EDR (Ellrod Eddy Dissipation Rate) 0.15 à 0.44 m^(2/3)/s",
            "SEVERE_CAT": "EDR >= 0.44 m^(2/3)/s (Accélération verticale delta_g > 1.0 g)",
        },
        operational_impacts=[
            "Risque de blessures pour les passagers et l'équipage en cabine",
            "Contraintes structurales sur la voilure",
        ],
        flight_recommendations=[
            "Allumer le signal d'attache des ceintures",
            "Changer de niveau de vol (+/- 2000 ft) pour sortir de la couche de cisaillement",
        ],
        references=["ICAO Doc 9837 Manual on Low-level Wind Shear and Turbulence", "Ellrod & Knapp (1992) WAF"],
    ),
    "airframe_icing": AviationHazardInfo(
        key="airframe_icing",
        name="Airframe Icing (Givrage de la Cellule)",
        category="ICING",
        physical_explanation=(
            "Le givrage en vol survient lorsque l'avion traverse des nuages contenant de l'eau liquide surfondue (SLW / FZDZ / FZRA) "
            "entre 0°C et -40°C. La frappe des gouttelettes sur le bord d'attaque provoque leur congélation instantanée (Givre blanc / Rime Ice) "
            "ou leur étalement puis congélation (Verglas clair / Clear Ice)."
        ),
        governing_equation=r"\text{Rate}_{\text{icing}} = E \cdot v_{\text{TAS}} \cdot \text{LWC}",
        icao_thresholds={
            "LIGHT": "LWC 0.1 - 0.6 g/m³ (Accumulation lente, les systèmes anti-givrage gèrent aisément)",
            "MODERATE": "LWC 0.6 - 1.2 g/m³",
            "SEVERE": "LWC > 1.2 g/m³ ou pluie verglaçante FZRA (Congélation au-delà des zones protégées)",
        },
        operational_impacts=[
            "Augmentation de la traînée aérodynamique",
            "Diminution drastique de la portance",
            "Décrochage prématuré",
        ],
        flight_recommendations=[
            "Activer les de-icing boot / heated leading edges",
            "Décrocher du niveau de vol en demandant une descente hors de la couche nuageuse",
        ],
        references=["ICAO Annex 3 Chapter 3", "FAA Aviation Weather Handbook Chapter 19"],
    ),
    "microburst_windshear": AviationHazardInfo(
        key="microburst_windshear",
        name="Microburst & Low-Level Wind Shear (Rafale Descendante & Cisaillement)",
        category="CONVECTION",
        physical_explanation=(
            "Un microburst est une puissante colonne d'air froid descendant (downburst < 4 km de large) issue d'un orage, "
            "s'étalant au sol à grande vitesse (vents > 50 kt). L'avion rencontre d'abord un fort vent debout (Headwind), "
            "suivi immédiatement d'une perte soudaine de vent debout et d'un vent arrière (Tailwind) avec fort courant descendant, provoquant une perte d'altitude critique en phase de finale."
        ),
        governing_equation=r"\Delta V_{\text{airspeed}} = u_{\text{headwind}} - u_{\text{tailwind}} > 30\text{ kt}",
        icao_thresholds={
            "MICROBURST_ALERT": "Gain/perte de vitesse de vent debout > 30 kt à moins de 1500 ft AGL",
        },
        operational_impacts=["Perte catastrophique d'altitude lors de l'atterrissage/décollage"],
        flight_recommendations=["Remise des gaz immédiate (Go-Around) pleine puissance Windshear Escape Maneuver"],
        references=["ICAO Doc 9837", "FAA Advisory Circular AC 00-54"],
    ),
}


class AviationHazardEngine:
    """Moteur d'évaluation scientifique des risques météo pour l'aviation."""

    @classmethod
    def get_hazard(cls, key: str) -> AviationHazardInfo | None:
        return AVIATION_HAZARDS_REGISTRY.get(key.lower())

    @classmethod
    def list_hazards(cls) -> list[str]:
        return list(AVIATION_HAZARDS_REGISTRY.keys())
