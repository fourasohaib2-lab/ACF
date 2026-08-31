"""
Atmospheric Complexity Framework (ACF)

MODELS Package

Numerical Weather Prediction (NWP) model drivers and ingestion adapters for AROME, ARPEGE, ALADIN, GFS, IFS, ERA5, WRF, and ICON.
"""

from acf.models.aladin import ALADINIngestionAdapter
from acf.models.arome import AROMEIngestionAdapter
from acf.models.arpege import ARPEGEIngestionAdapter
from acf.models.base_model import BaseWeatherModel
from acf.models.forecast_config import ForecastConfig

__all__ = [
    "ALADINIngestionAdapter",
    "AROMEIngestionAdapter",
    "ARPEGEIngestionAdapter",
    "BaseWeatherModel",
    "ForecastConfig",
]
