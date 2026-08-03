"""
Ocean Global Circulation Model (AMOC, Gulf Stream, ENSO)
"""

from typing import Any, Dict


class OceanCirculationModel:
    """Modèle de la circulation générale océanique (AMOC, Gulf Stream, ENSO)."""

    @classmethod
    def amoc_transport_sverdrup(cls) -> Dict[str, Any]:
        """Retourne le débit de l'AMOC en Sverdrup (1 Sv = 10^6 m^3/s)."""
        return {"amoc_strength_sv": 17.5, "status": "AMOC_OPERATIONAL"}
