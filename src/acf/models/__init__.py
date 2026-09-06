"""
Atmospheric Complexity Framework (ACF)

MODELS Package

Numerical Weather Prediction (NWP) model drivers and ingestion adapters for AROME, ARPEGE, ALADIN, ERA5, WRF, ICON, and OpenIFS.

NOTE (correction — registry/docstring overclaim, found during the
post-model4d audit, 2026-09-06): this header used to also list "GFS"
and "IFS" - GFS has no real adapter class anywhere in this codebase
(verified via grep), and OpenIFS - ECMWF's own openly-licensed IFS
release, real code and parameter table (see `OpenIFSIngestionAdapter`'s
own docstring) - is the real IFS-family adapter this package has, not
a separate "IFS" one. Separately, WRFIngestionAdapter/
ICONIngestionAdapter/OpenIFSIngestionAdapter/ERA5Model were already
real (each package-level `acf.models.wrf`/`icon`/`openifs` already
re-exports its own adapter) but were never re-exported from this
top-level package - `from acf.models import WRFIngestionAdapter` used
to `ImportError` despite the class genuinely existing. Both corrected:
the docstring now names only what's real, and the 4 already-real
adapters are re-exported here too, matching AROME/ALADIN/ARPEGE.
"""

from acf.models.aladin import ALADINIngestionAdapter
from acf.models.arome import AROMEIngestionAdapter
from acf.models.arpege import ARPEGEIngestionAdapter
from acf.models.base_model import BaseWeatherModel
from acf.models.forecast_config import ForecastConfig
from acf.models.icon import ICONIngestionAdapter
from acf.models.implementations.era5 import ERA5Model
from acf.models.openifs import OpenIFSIngestionAdapter
from acf.models.wrf import WRFIngestionAdapter

__all__ = [
    "ALADINIngestionAdapter",
    "AROMEIngestionAdapter",
    "ARPEGEIngestionAdapter",
    "BaseWeatherModel",
    "ERA5Model",
    "ForecastConfig",
    "ICONIngestionAdapter",
    "OpenIFSIngestionAdapter",
    "WRFIngestionAdapter",
]
