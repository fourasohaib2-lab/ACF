"""
Ice Sheet Dynamics Model (Greenland & Antarctica)
"""


class IceSheetDynamics:
    """Modèle d'écoulement et de dynamique des calottes glaciaires (Groenland & Antarctique)."""

    @classmethod
    def sea_level_equivalent_contribution(cls, ice_loss_gt: float) -> float:
        """361.8 Gt d'eau douce = 1 mm d'élévation du niveau de la mer."""
        return ice_loss_gt / 361.8
