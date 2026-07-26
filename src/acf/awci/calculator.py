"""
AWCI Calculator
===============

Aviation Weather Complexity Index calculator.
"""

from typing import Dict, Optional, Any
import numpy as np

from .weights import WeightsManager
from .normalizer import Normalizer


class AWCICalculator:
    """
    Aviation Weather Complexity Index (AWCI) calculator.
    
    Combines multiple atmospheric modules into a single
    complexity score (0-100) with decomposition.
    """
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        Initialize AWCI calculator.
        
        Parameters
        ----------
        weights : dict, optional
            Custom weights for each module.
            Default weights are used if not provided.
        """
        self.weights_manager = WeightsManager(weights)
        self.normalizer = Normalizer()
        self._last_decomposition = None
    
    def calculate_module_scores(self, data: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate scores for each module from input data.
        
        Parameters
        ----------
        data : dict
            Input meteorological data with keys:
            - temperature: Temperature in Kelvin
            - specific_humidity: Specific humidity in kg/kg
            - wind_speed: Wind speed in m/s
            - cape: CAPE in J/kg
            - cin: CIN in J/kg
            - precipitation: Precipitation in mm/h
            - pressure: Pressure in hPa
            - altitude: Altitude in meters
            - confidence: Forecast confidence in %
            - temporal_change: Rate of change
            
        Returns
        -------
        dict
            Module scores in [0, 1]
        """
        scores = {}
        
        # Dynamic module - based on wind
        wind = data.get('wind_speed', 0.0)
        scores['dynamic'] = self.normalizer.normalize_wind(wind)
        
        # Thermodynamic module - based on temperature and humidity
        temp = data.get('temperature', 273.15)
        hum = data.get('specific_humidity', 0.001)
        
        # Combine temperature and humidity for thermodynamic complexity
        temp_norm = self.normalizer.normalize_temperature(temp)
        hum_norm = self.normalizer.normalize_humidity(hum)
        scores['thermodynamic'] = 0.5 * temp_norm + 0.5 * hum_norm
        
        # Convective module - based on CAPE and CIN
        cape = data.get('cape', 0.0)
        cin = data.get('cin', 0.0)
        cape_norm = self.normalizer.normalize_cape(cape)
        cin_norm = self.normalizer.normalize_cin(cin)
        scores['convective'] = 0.7 * cape_norm + 0.3 * cin_norm
        
        # Microphysical module - based on precipitation
        precip = data.get('precipitation', 0.0)
        scores['microphysical'] = self.normalizer.normalize_precipitation(precip)
        
        # Topographic module - based on altitude
        altitude = data.get('altitude', 0.0)
        scores['topographic'] = self.normalizer.normalize_topographic(altitude)
        
        # Temporal module - rate of change
        temporal = data.get('temporal_change', 0.0)
        scores['temporal'] = self.normalizer.normalize_temporal(temporal)
        
        # Confidence module
        confidence = data.get('confidence', 100.0)
        # Lower confidence = higher complexity
        scores['confidence'] = 1.0 - self.normalizer.normalize_confidence(confidence)
        
        return scores
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate AWCI from input data.
        
        Parameters
        ----------
        data : dict
            Input meteorological data.
            
        Returns
        -------
        dict
            {
                'awci': float (0-100),
                'decomposition': dict,
                'level': str,
                'confidence': float
            }
        """
        # Calculate module scores
        module_scores = self.calculate_module_scores(data)
        
        # Apply weights
        weighted_sum = 0.0
        decomposition = {}
        
        for module, score in module_scores.items():
            weight = self.weights_manager.get_weight(module)
            weighted = score * weight
            weighted_sum += weighted
            decomposition[module] = round(weighted * 100, 1)
        
        # Scale to 0-100
        awci_score = round(weighted_sum * 100, 1)
        
        # Determine level
        level = self._get_level(awci_score)
        
        # Store decomposition for later use
        self._last_decomposition = decomposition
        
        return {
            'awci': awci_score,
            'decomposition': decomposition,
            'level': level,
            'confidence': data.get('confidence', 100.0),
            'module_scores': {k: round(v * 100, 1) for k, v in module_scores.items()}
        }
    
    def _get_level(self, score: float) -> str:
        """
        Determine complexity level from AWCI score.
        
        Parameters
        ----------
        score : float
            AWCI score (0-100)
            
        Returns
        -------
        str
            Complexity level
        """
        if score < 20:
            return "Very Low"
        elif score < 35:
            return "Low"
        elif score < 50:
            return "Moderate"
        elif score < 65:
            return "High"
        elif score < 85:
            return "Very High"
        else:
            return "Extreme"
    
    def get_decomposition(self) -> Dict[str, float]:
        """
        Get the decomposition from the last calculation.
        
        Returns
        -------
        dict
            Decomposition of AWCI by module
        """
        return self._last_decomposition or {}
    
    def reset(self):
        """Reset the calculator to default state."""
        self._last_decomposition = None
        self.weights_manager.reset()
