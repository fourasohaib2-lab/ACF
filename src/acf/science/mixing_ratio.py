"""
Mixing Ratio
============

Formula:
    w = q / (1 - q)

where:
    w = mixing ratio (kg/kg)
    q = specific humidity (kg/kg)
"""

class MixingRatio:
    """Mixing ratio calculator."""
    
    @staticmethod
    def calculate(specific_humidity: float) -> float:
        """
        Calculate mixing ratio from specific humidity.
        
        Parameters
        ----------
        specific_humidity : float
            Specific humidity (kg/kg) in [0, 1)
            
        Returns
        -------
        float
            Mixing ratio (kg/kg)
        """
        if specific_humidity < 0.0 or specific_humidity >= 1.0:
            raise ValueError("Specific humidity must be in [0, 1)")
        return specific_humidity / (1.0 - specific_humidity)
