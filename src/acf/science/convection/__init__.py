"""
Atmospheric Complexity Framework (ACF)

Convection Science Package

Migrated 2026-09-21 (Phase 2 of the ACF science/ per-domain
reorganization - see
docs/architecture/acf_awci_architecture_gap_analysis.md's own §4
section) from 8 flat modules directly under ``acf.science`` into this
subpackage, matching the blueprint's own ``science/convection/``
layer. Real module names kept as-is (``parcel_ascent.py`` for the
blueprint's own illustrative ``parcel.py``). ``acf.science.<module>``
is kept as a real backward-compatible re-export for every one of them.

``storm_relative_helicity.py``, ``storm_motion.py``, and
``bulk_wind_shear.py`` are not named in the blueprint's own smaller
illustrative sketch, but are real, standard severe-convective-storm
kinematic diagnostics (SRH, storm motion, bulk shear) computed
alongside CAPE/CIN in operational forecasting - placed here by real
role, a disclosed decision following the same precedent established
throughout the AWCI migration.

Phase 7 added ``severe_weather.py`` (``SevereWeather``, composite
severe-convection indices combining CAPE/CIN, vertical wind shear and
storm-relative helicity - the same real role as the three modules
above, verified against NOAA SPC's own mesoanalysis parameter
definitions).
"""

from acf.science.convection.bulk_wind_shear import BulkWindShear
from acf.science.convection.cape import CAPE
from acf.science.convection.cin import CIN
from acf.science.convection.lcl import LCL
from acf.science.convection.lfc import LFC
from acf.science.convection.parcel_ascent import ParcelAscentEngine
from acf.science.convection.severe_weather import SevereWeather
from acf.science.convection.storm_motion import StormMotion
from acf.science.convection.storm_relative_helicity import StormRelativeHelicity

__all__ = [
    "BulkWindShear",
    "CAPE",
    "CIN",
    "LCL",
    "LFC",
    "ParcelAscentEngine",
    "SevereWeather",
    "StormMotion",
    "StormRelativeHelicity",
]
