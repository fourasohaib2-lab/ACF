"""
Atmospheric Complexity Framework (ACF)

Cloud AI Reasoning Engine
"""

from typing import Any, Dict, List
from acf.science.clouds.thermodynamics import CloudThermodynamicsEngine
from acf.science.clouds.severe_weather import SevereWeatherCloudModule
from acf.science.clouds.registry import CloudScientificRegistry


class CloudReasoningEngine:
    """
    Moteur d'intelligence artificielle explicative pour les nuages et processus orageux.
    """

    def __init__(self):
        self.thermo = CloudThermodynamicsEngine()
        self.severe = SevereWeatherCloudModule()

    def explain_cumulonimbus_formation(
        self,
        cape_j_kg: float,
        surface_humidity_pct: float,
        low_level_convergence_s1: float,
        shear_0_6km_m_s: float,
    ) -> Dict[str, Any]:
        """
        Répond scientifiquement à la question 'Pourquoi formation d'un Cumulonimbus ?'
        """
        reasons: List[str] = []
        physical_mechanisms: List[str] = []

        # 1. Instabilité Thermodynamique
        if cape_j_kg > 1000:
            reasons.append(f"CAPE élevé ({cape_j_kg:.1f} J/kg > 1000 J/kg) procurant une forte énergie potentielle d'ascendance.")
            physical_mechanisms.append("Poussée d'Archimède positive accélérant la parcelle d'air vers la tropopause (w_max = sqrt(2*CAPE)).")
        else:
            reasons.append(f"CAPE modéré à faible ({cape_j_kg:.1f} J/kg).")

        # 2. Humidité en basse couche
        if surface_humidity_pct > 70:
            reasons.append(f"Humidité relative élevée en basse couche ({surface_humidity_pct:.0f}% > 70%), abaissant le LCL.")
            physical_mechanisms.append("Condensation précoce entraînant la libération massive de chaleur latente de vaporisation (Lv).")

        # 3. Convergence basse couche
        if low_level_convergence_s1 > 1e-5:
            reasons.append("Convergence horizontale du vent en basse couche forçant l'ascendance mécanique au-dessus du LFC.")
            physical_mechanisms.append("Équation de continuité de masse (d(rho)/dt + div(rho*V) = 0).")

        # 4. Cisaillement vertical du vent
        if shear_0_6km_m_s > 15:
            reasons.append(f"Fort cisaillement vertical du vent (0-6km: {shear_0_6km_m_s:.1f} m/s > 15 m/s) séparant le courant ascendant du courant descendant.")
            physical_mechanisms.append("Organisation de la cellule en orage multicellulaire ou supercellulaire à longue durée de vie.")

        governing_laws = [
            CloudScientificRegistry.get("cape_integral"),
            CloudScientificRegistry.get("lcl_altitude"),
            CloudScientificRegistry.get("convective_mass_flux"),
        ]
        laws_summary = [law.summary() for law in governing_laws if law]

        return {
            "question": "Pourquoi formation d'un Cumulonimbus ?",
            "verdict": "Conditions très favorables à la convection profonde" if (cape_j_kg > 1000 and surface_humidity_pct > 65) else "Conditions marginales",
            "justification": reasons,
            "physical_mechanisms": physical_mechanisms,
            "governing_laws": laws_summary,
        }

    def reason_about_cloud(self, cloud_genre: str, environmental_state: Dict[str, float]) -> Dict[str, Any]:
        """
        Fournit une explication physique personnalisée pour tout genre de nuage.
        """
        cape = environmental_state.get("cape", 0.0)
        rh = environmental_state.get("humidity", 50.0)

        if "cumulonimbus" in cloud_genre.lower():
            conv = environmental_state.get("convergence", 2e-5)
            shear = environmental_state.get("shear", 20.0)
            return self.explain_cumulonimbus_formation(cape, rh, conv, shear)

        return {
            "question": f"Pourquoi formation d'un {cloud_genre} ?",
            "verdict": "Formation nuageuse standard",
            "justification": [
                f"Humidité relative de {rh}%.",
                f"Énergie convective (CAPE) de {cape} J/kg.",
            ],
        }
