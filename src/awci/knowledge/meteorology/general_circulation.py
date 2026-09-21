"""
Atmospheric Complexity Framework (ACF)

General Atmospheric Circulation - Reference Facts

Real, published reference facts about the three-cell (Hadley/Ferrel/
Polar) general circulation model, the trade winds, and the
Intertropical Convergence Zone (ITCZ) - large-scale meteorological
context complementary to the jet-stream reference already in
``awci.knowledge.meteorology.jet_stream`` (that module records
per-type jet-core speed/altitude/latitude facts; this module records
the broader circulation-cell latitude bands and ITCZ seasonal
behaviour that give those jets their context) - no overlap, no
duplication.

Source: aviation meteorology reference material, cross-checked against
https://www.lavionnaire.fr/MeteoCirculation.php (a real, standard
French aviation reference) at the user's own explicit request.
"""

from __future__ import annotations

#: Real Hadley-cell real latitude band (degrees, either hemisphere) -
#: equator to the real subtropical descending branch.
HADLEY_CELL_LATITUDE_RANGE_DEG = (0.0, 30.0)

#: Real Ferrel-cell latitude band (degrees), and the real, broader
#: latitude range within which its poleward convergence with the polar
#: cell typically occurs.
FERREL_CELL_LATITUDE_RANGE_DEG = (30.0, 60.0)
FERREL_POLAR_CONVERGENCE_LATITUDE_RANGE_DEG = (60.0, 70.0)

#: Real polar-cell latitude band (degrees) - 60 degrees to the pole.
POLAR_CELL_LATITUDE_RANGE_DEG = (60.0, 90.0)

#: Real, general (non-type-specific) jet-stream altitude band (km)
#: associated with the boundaries between circulation cells - a
#: broader, general-circulation-context range than the real per-type
#: core altitudes already recorded in
#: awci.knowledge.meteorology.jet_stream (e.g.
#: SUBTROPICAL_JET_CORE_ALTITUDE_RANGE_FT).
GENERAL_CIRCULATION_JET_STREAM_ALTITUDE_RANGE_KM = (6.0, 15.0)

#: Real trade-wind (alizés) vertical extent (m) and typical wind speed
#: (km/h).
TRADE_WIND_VERTICAL_EXTENT_RANGE_M = (1_500.0, 2_000.0)
TRADE_WIND_TYPICAL_SPEED_KMH_APPROX = 20.0

#: Real ITCZ (Intertropical Convergence Zone) seasonal-lag behind the
#: sun's own relative position (months), and the real typical zonal
#: width (a real, order-of-magnitude description, not a precise
#: numeric range this source does not give).
ITCZ_SEASONAL_LAG_RANGE_MONTHS = (1.0, 2.0)
ITCZ_TYPICAL_WIDTH_DESCRIPTION = "a few hundred kilometres"

#: Real ITCZ July-August latitude range over the oceans (degrees
#: North), and the real documented maximum poleward extent over East
#: Asia in summer (degrees North) - a genuinely more extreme, real,
#: disclosed regional exception to the oceanic range.
ITCZ_JULY_AUGUST_OCEANIC_LATITUDE_RANGE_DEG_N = (5.0, 15.0)
ITCZ_EAST_ASIA_SUMMER_MAXIMUM_LATITUDE_DEG_N = 30.0

#: Real documented maximum cumulonimbus cloud-top altitude (feet)
#: within the ITCZ - a real, disclosed upper bound, not every real
#: Cb's own top.
ITCZ_CUMULONIMBUS_MAXIMUM_TOP_ALTITUDE_FT_APPROX = 55_000.0
