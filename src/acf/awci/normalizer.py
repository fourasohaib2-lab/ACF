"""
AWCI Normalizer
===============

Normalizes variables to [0, 1] range for AWCI calculation.
"""



class Normalizer:
    """
    Normalizes meteorological variables to [0, 1].
    
    Each variable has its own normalization function based on
    typical ranges.
    """
    
    @staticmethod
    def normalize_temperature(value: float, is_kelvin: bool = True) -> float:
        """
        Normalize temperature to [0, 1].
        
        Range: -30°C to +50°C (243K to 323K)
        """
        if is_kelvin:
            T_c = value - 273.15
        else:
            T_c = value
        
        # Clip to range
        T_c = max(-30.0, min(50.0, T_c))
        
        # Normalize to [0, 1]
        return (T_c + 30.0) / 80.0
    
    @staticmethod
    def normalize_wind(value: float) -> float:
        """
        Normalize wind speed to [0, 1].
        
        Range: 0 to 50 m/s
        """
        value = max(0.0, min(50.0, value))
        return value / 50.0
    
    @staticmethod
    def normalize_humidity(value: float) -> float:
        """
        Normalize specific humidity to [0, 1].
        
        Range: 0 to 0.03 kg/kg
        """
        value = max(0.0, min(0.03, value))
        return value / 0.03
    
    @staticmethod
    def normalize_cape(value: float) -> float:
        """
        Normalize CAPE to [0, 1].
        
        Range: 0 to 5000 J/kg
        """
        value = max(0.0, min(5000.0, value))
        return value / 5000.0
    
    @staticmethod
    def normalize_cin(value: float) -> float:
        """
        Normalize CIN to [0, 1].
        
        Range: 0 to -500 J/kg (negative values)
        """
        # CIN is negative, convert to positive for normalization
        value = abs(value)
        value = max(0.0, min(500.0, value))
        return value / 500.0
    
    @staticmethod
    def normalize_precipitation(value: float) -> float:
        """
        Normalize precipitation rate to [0, 1].
        
        Range: 0 to 50 mm/h
        """
        value = max(0.0, min(50.0, value))
        return value / 50.0
    
    @staticmethod
    def normalize_pressure(value: float) -> float:
        """
        Normalize pressure to [0, 1].
        
        Range: 800 to 1050 hPa
        """
        value = max(800.0, min(1050.0, value))
        return (value - 800.0) / 250.0
    
    @staticmethod
    def normalize_topographic(value: float, max_altitude: float = 3000.0) -> float:
        """
        Normalize topographic complexity to [0, 1].
        
        Range: 0 to max_altitude meters
        """
        value = max(0.0, min(max_altitude, value))
        return value / max_altitude
    
    @staticmethod
    def normalize_confidence(value: float) -> float:
        """
        Normalize confidence to [0, 1].
        
        Range: 0 to 100%
        """
        value = max(0.0, min(100.0, value))
        return value / 100.0
    
    @staticmethod
    def normalize_temporal(value: float, max_change: float = 20.0) -> float:
        """
        Normalize temporal evolution to [0, 1].
        
        Range: 0 to max_change units
        """
        value = max(0.0, min(max_change, value))
        return value / max_change
    
    @staticmethod
    def normalize_specific_humidity(value: float) -> float:
        """
        Normalize specific humidity to [0, 1].
        
        Range: 0 to 0.03 kg/kg
        """
        return Normalizer.normalize_humidity(value)
