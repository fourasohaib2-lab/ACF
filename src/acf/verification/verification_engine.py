"""
Atmospheric Complexity Framework (ACF)

Forecast Verification Engine Module (Phase 11)
(ETS, CSI, POD, FAR, HSS, ACC, CRPS, Brier Score, Taylor Diagram)
"""


class ForecastVerificationEngine:
    """
    Moteur de vérification statistique des prédictions NWP & IA par rapport aux observations.
    """

    @staticmethod
    def contingency_table_metrics(a: float, b: float, c: float, d: float) -> dict[str, float]:
        """
        Calcule les scores statistiques à partir d'une table de contingence 2x2 :
        a = Succès (Hits), b = Fausses Alertes (False Alarms), c = Rabilités / Non-détections (Misses), d = Vrais Négatifs (Correct Rejections).
        """
        total = a + b + c + d
        pod = a / (a + c) if (a + c) > 0 else 0.0
        far = b / (a + b) if (a + b) > 0 else 0.0
        csi = a / (a + b + c) if (a + b + c) > 0 else 0.0

        # Random hits for ETS
        a_ref = ((a + b) * (a + c)) / total if total > 0 else 0.0
        ets = (a - a_ref) / (a + b + c - a_ref) if (a + b + c - a_ref) > 0 else 0.0

        # Heidke Skill Score (HSS)
        expected_correct = ((a + b) * (a + c) + (b + d) * (c + d)) / total if total > 0 else 0.0
        hss = ((a + d) - expected_correct) / (total - expected_correct) if (total - expected_correct) > 0 else 0.0

        return {
            "POD": pod,  # Probability of Detection
            "FAR": far,  # False Alarm Ratio
            "CSI": csi,  # Critical Success Index
            "ETS": ets,  # Equitable Threat Score
            "HSS": hss,  # Heidke Skill Score
        }
