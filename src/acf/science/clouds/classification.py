"""
Atmospheric Complexity Framework (ACF)

Cloud Classification Engine
"""

from typing import Any, Dict


class CloudClassificationEngine:
    """
    Moteur de classification scientifique automatique des genres et espèces de nuages selon la nomenclature OMM (WMO International Cloud Atlas).
    """

    GENRES = {
        "High": ["Cirrus", "Cirrostratus", "Cirrocumulus"],
        "Middle": ["Altostratus", "Altocumulus"],
        "Low": ["Stratus", "Stratocumulus", "Nimbostratus"],
        "Convective": ["Cumulus", "Cumulus congestus", "Cumulonimbus"],
    }

    def classify(
        self,
        base_altitude_m: float,
        top_altitude_m: float,
        temperature_c: float,
        relative_humidity: float,
        radar_reflectivity_dbz: float = 0.0,
        cloud_optical_depth: float = 1.0,
        cape_j_kg: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Classifie automatiquement le nuage en fonction de ses propriétés physiques, de son altitude, de son optique et du radar.
        """
        thickness = top_altitude_m - base_altitude_m

        # Convective clouds
        if cape_j_kg > 1000 or radar_reflectivity_dbz > 40 or thickness > 6000:
            genre = "Cumulonimbus"
            family = "Convective"
            description = "Nuage convectif de grande extension verticale capable de produire de l'orage et des grêlons."
        elif cape_j_kg > 300 or thickness > 2500:
            genre = "Cumulus congestus"
            family = "Convective"
            description = "Nuage convectif bourgeonnant à fort développement vertical."
        elif thickness > 1000 and base_altitude_m < 2000 and relative_humidity > 0.8:
            if radar_reflectivity_dbz > 20:
                genre = "Nimbostratus"
                family = "Low"
                description = "Couche nuageuse sombre continue produisant de la pluie ou de la neige régulières."
            else:
                genre = "Stratocumulus"
                family = "Low"
                description = "Banc ou couche de galets ou rouleaux nuageux sombres."
        elif base_altitude_m < 2000:
            if thickness < 500:
                genre = "Stratus"
                family = "Low"
                description = "Couche nuageuse grise très basse et uniforme ressemblant à du brouillard élevé."
            else:
                genre = "Cumulus"
                family = "Convective"
                description = "Nuage séparé à contours net se développant sous forme de mamelons."
        elif 2000 <= base_altitude_m < 6000:
            if cloud_optical_depth > 10:
                genre = "Altostratus"
                family = "Middle"
                description = "Nappe nuageuse grisâtre striée couvrant le ciel et noyant le Soleil."
            else:
                genre = "Altocumulus"
                family = "Middle"
                description = "Banc de petits nuages blancs et gris en forme de galets ou de rouleaux."
        else:
            # High clouds (> 6000 m)
            if cloud_optical_depth < 1.0:
                genre = "Cirrus"
                family = "High"
                description = "Nuage élevé sous forme de filaments blancs et délicats constitués de cristaux de glace."
            elif cloud_optical_depth < 3.0:
                genre = "Cirrostratus"
                family = "High"
                description = "Voile nuageux transparent et blanchâtre produisant des phénomènes d'halo autour du Soleil."
            else:
                genre = "Cirrocumulus"
                family = "High"
                description = "Banc de petits éléments nuageux blancs sans ombre propre."

        return {
            "genre": genre,
            "family": family,
            "base_altitude_m": base_altitude_m,
            "top_altitude_m": top_altitude_m,
            "thickness_m": thickness,
            "temperature_c": temperature_c,
            "optical_depth": cloud_optical_depth,
            "radar_dbz": radar_reflectivity_dbz,
            "description": description,
        }
