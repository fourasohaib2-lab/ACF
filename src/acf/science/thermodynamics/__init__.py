"""
Atmospheric Complexity Framework (ACF)

Thermodynamics Science Package

Migrated 2026-09-21 (Phase 1 of the ACF science/ per-domain
reorganization - see
docs/architecture/acf_awci_architecture_gap_analysis.md's own §4
section) from 21 flat modules directly under ``acf.science`` into this
subpackage, matching the blueprint's own ``science/thermodynamics/``
layer (its "initial atmospheric priority"). Real module names kept
as-is. ``acf.science.<module>`` is kept as a real backward-compatible
re-export for every one of them.
"""

from acf.science.thermodynamics.air_density import AirDensity
from acf.science.thermodynamics.dewpoint import DewPoint
from acf.science.thermodynamics.dry_static_energy import DryStaticEnergy
from acf.science.thermodynamics.equivalent_potential_temperature import EquivalentPotentialTemperature
from acf.science.thermodynamics.geopotential_height import GeopotentialHeight
from acf.science.thermodynamics.humidity import Humidity
from acf.science.thermodynamics.hypsometric_equation import HypsometricEquation
from acf.science.thermodynamics.mixing_ratio import MixingRatio
from acf.science.thermodynamics.moist_static_energy import MoistStaticEnergy
from acf.science.thermodynamics.potential_temperature import PotentialTemperature
from acf.science.thermodynamics.pressure import Pressure
from acf.science.thermodynamics.relative_humidity import RelativeHumidity
from acf.science.thermodynamics.saturation_mixing_ratio import SaturationMixingRatio
from acf.science.thermodynamics.saturation_vapor_pressure import SaturationVaporPressure
from acf.science.thermodynamics.specific_humidity import SpecificHumidity
from acf.science.thermodynamics.temperature import Temperature
from acf.science.thermodynamics.thermodynamics import Thermodynamics
from acf.science.thermodynamics.vapor_pressure import VaporPressure
from acf.science.thermodynamics.virtual_potential_temperature import VirtualPotentialTemperature
from acf.science.thermodynamics.virtual_temperature import VirtualTemperature
from acf.science.thermodynamics.wet_bulb_temperature import WetBulbTemperature

__all__ = [
    "AirDensity",
    "DewPoint",
    "DryStaticEnergy",
    "EquivalentPotentialTemperature",
    "GeopotentialHeight",
    "Humidity",
    "HypsometricEquation",
    "MixingRatio",
    "MoistStaticEnergy",
    "PotentialTemperature",
    "Pressure",
    "RelativeHumidity",
    "SaturationMixingRatio",
    "SaturationVaporPressure",
    "SpecificHumidity",
    "Temperature",
    "Thermodynamics",
    "VaporPressure",
    "VirtualPotentialTemperature",
    "VirtualTemperature",
    "WetBulbTemperature",
]
