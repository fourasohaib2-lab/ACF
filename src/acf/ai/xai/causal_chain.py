"""
Atmospheric Complexity Framework (ACF)

Physical Causal Chain Generator Module
"""

from typing import List


class CausalChainGenerator:
    """Générateur de la chaîne d'explication causale physique."""

    @classmethod
    def generate_causal_chain(cls) -> List[str]:
        return [
            "1. SST Anomaly +2.3°C over Gulf Stream",
            "2. Moisture Transport IVT +45%",
            "3. Surface CAPE 2300 J/kg",
            "4. Vertical Wind Shear 35 kt",
            "5. Stratospheric PV Anomaly Intrusion",
        ]
