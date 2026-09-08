"""
ACF Event Engine — weather event objects with a real lifecycle
==================================================================

Explicit user request: the "Prompt Maître ACF v2.0" master specification's
sections 12-14 and 34 describe formal weather event objects
(ThunderstormEvent, CycloneEvent, HeavyRainEvent, ...) with a real
lifecycle (DETECTED -> ANALYZED -> CONFIRMED -> VERIFIED -> CERTIFIED ->
PUBLISHED, or DETECTED -> REJECTED) - reports/ACF_MASTER_AUDIT_v2.md
found this genuinely absent: the existing "events" code
(acf.aeos.events.event_bus, acf.digital_twin.events.cascade_engine) is
an internal SYSTEM event bus (application signals), a different concept
from a meteorological event object.

What's built here
--------------------
- Event: the section 12 contract (event_id, type, geometry, start_time,
  end_time, intensity, probability, confidence, supporting_parameters,
  supporting_models, observations, uncertainty, provenance, status),
  reusing acf.core.contracts.Provenance/UncertaintyInfo rather than
  duplicating them, with a real state machine enforcing the section 13
  lifecycle - transition_to() raises for any transition not in that
  diagram, not just anything a caller happens to set.
- detectors/: real threshold-based detection from ACF's own real
  Complexity Engine field output (acf.awci.spatial_field.
  compute_real_complexity_field()'s wind_speed_field/temperature_field/
  specific_humidity_field/pressure_field_hpa - genuine
  CoupledEarthSolver output, not synthetic).

Honest scope - what is NOT built here, and why
-----------------------------------------------
Only 2 of the master spec's 8 named event types have a real, defensible
detector: StrongWindEvent (a direct threshold on real wind_speed_field)
and FogEvent (real relative humidity, computed via MetPy from real
specific_humidity/temperature/pressure - not a synthetic proxy). The
other 6 need data ACF's real solver output does not currently provide
per grid point:
- ThunderstormEvent/convection needs real CAPE - the Complexity Engine's
  real fields feed AWCICalculator's convective module from raw
  temperature/wind/humidity only, no real per-point CAPE is computed
  anywhere in acf.awci today.
- CycloneEvent needs vorticity/pressure-minimum tracking over a real
  time series - a genuinely harder detection problem than a threshold,
  not attempted here.
- HeavyRainEvent, SnowEvent, HailEvent need real precipitation, which
  is not in CoupledEarthSolver's state dict at all (confirmed: state
  keys are T, P, U, V, q, O3, CO2, SST, Salinity, U_ocean, V_ocean,
  Ice, Soil, Soil_Temp, Biomass - no precipitation field).
- DustEvent needs real aerosol concentration data, which does not exist
  anywhere in ACF's real solver output either.

Building a detector for any of these without real supporting data would
mean inventing a proxy formula and presenting it as if it detects the
named phenomenon - exactly what this project's audits exist to prevent.
"""

from acf.events.detectors.fog_detector import detect_fog_favorable_events
from acf.events.detectors.wind_detector import detect_strong_wind_events
from acf.events.event import Event, IllegalEventTransitionError

__all__ = ["Event", "IllegalEventTransitionError", "detect_strong_wind_events", "detect_fog_favorable_events"]
