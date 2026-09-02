"""
ACF Fire Weather Index
=========================

Specialized Weather Services layer (docs/ACF_MASTER_UNIFIED_ARCHITECTURE.md's
"20. SPECIALIZED WEATHER SERVICES" -> "FIRE WEATHER: fire indices, fuel
conditions, smoke transport"). Explicit user request "vas-y, construis
fire_weather/", following docs/ACF_ARCHITECTURE_TARGET_GAP_MAP.md
flagging this package as entirely absent.

What this is - and, importantly, what it deliberately is NOT
------------------------------------------------------------------
Real, published fire-danger indices exist with specific numeric
formulas - the Fosberg Fire Weather Index (Fosberg, 1978), the
Canadian Forest Fire Weather Index (FWI) System, the Australian
McArthur Forest Fire Danger Index (FFDI). This module does NOT
reproduce any one of them bit-for-bit: their exact published
coefficients are the kind of precise numeric detail that cannot be
independently verified against a primary source in this offline
environment, and fire danger is a domain where a subtly wrong
transcribed coefficient has real safety stakes - exactly the failure
mode this project's audits (docs/ACF_PHYSICS_GUARD_AUDIT_CHANGELOG.md)
exist to catch, not add.

Instead, `FireWeatherCalculator` is - explicitly, like
acf.awci.calculator.AWCICalculator's own INTERACTION_WEIGHTS before it
- an ACF-designed composite index: real, physically well-understood
drivers (low relative humidity, high wind speed, high temperature,
prolonged dryness since last precipitation - each independently
uncontroversial physics, not requiring a specific external formula to
justify), combined with weights and normalization ranges that are this
project's own documented design choice, not a reproduction of Fosberg/
FWI/FFDI's specific published numbers. If Fosberg FWI, the Canadian FWI
System, or McArthur FFDI are ever needed for real operational parity
with another agency's product, that requires implementing one of them
against its primary published source directly - not retrofitting this
module.
"""

from acf.fire_weather.calculator import FireWeatherCalculator

__all__ = ["FireWeatherCalculator"]
