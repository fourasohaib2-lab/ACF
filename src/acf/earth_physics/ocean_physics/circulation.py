"""
Ocean Global Circulation Model (AMOC, Gulf Stream, ENSO)
"""

from typing import Any


class OceanCirculationModel:
    """Modèle de la circulation générale océanique (AMOC, Gulf Stream, ENSO)."""

    @classmethod
    def amoc_transport_sverdrup(cls) -> dict[str, Any]:
        """
        Retourne le débit de l'AMOC en Sverdrup (1 Sv = 10^6 m^3/s).

        NOTE: takes no inputs and has no live ocean model or
        observation feed connected - 17.5 Sv is a plausible
        illustrative value (in the range of RAPID array observational
        estimates, ~17-18 Sv) but is NOT computed or fetched from real
        data. Marked explicitly rather than presented as if live.
        """
        return {"amoc_strength_sv": 17.5, "status": "AMOC_OPERATIONAL", "is_real_data": False}
