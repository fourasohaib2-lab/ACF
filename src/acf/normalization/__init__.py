"""
ACF Normalization & Interoperability Engine
==============================================

Layer 3 of the target architecture
(docs/ACF_MASTER_UNIFIED_ARCHITECTURE.md's "NORMALIZATION &
INTEROPERABILITY" - Variable naming, unit normalization, coordinate/
time/vertical/grid/projection normalization -> "Common ACF Data
Model"). Explicit user request "vas-y, construis normalization/",
following docs/ACF_ARCHITECTURE_TARGET_GAP_MAP.md flagging this
package as entirely absent.

What's built here (real, tested)
-----------------------------------
- units.convert_unit(): real unit conversion via MetPy's pint-based
  unit registry (same library/convention already used in
  science/parcel_ascent.py) - not a hand-rolled conversion-factor
  table.
- variable_names.to_cf_standard_name(): maps a model-specific short
  name (e.g. ECMWF's "t2m") to its real CF standard_name, by actually
  loading resources/standards/ecmwf/parameters.json and resources/
  standards/cf/cf_standard_names.json - both real, correct JSON tables
  that existed in this repo but were never loaded by any code before
  this (found while building this package, wired in rather than
  duplicated).
- normalizer.normalize_variable(): combines both into the single entry
  point a caller actually wants - "given this model's name/value/unit
  for a variable, what's its CF standard_name and value in CF units".

Honest scope - what this does NOT do
---------------------------------------
- No spatial/grid regridding (nearest/bilinear/conservative
  interpolation between grids) - that capability does not exist
  anywhere in ACF yet (see docs/ACF_ARCHITECTURE_TARGET_GAP_MAP.md's
  own note on this); acf.awci.path_sampling's nearest-neighbour
  sampling is the closest real building block today, built for a
  different purpose (sampling one field along a path, not
  regridding a whole dataset).
- No vertical-level interpolation (see acf.awci.vertical_field's own
  honest_limitation - native model levels only, everywhere in ACF).
- No time-axis resampling/interpolation.
- Variable-name coverage is limited to what resources/standards/
  ecmwf/parameters.json and cf_standard_names.json actually contain
  today (a handful of common surface variables) - not a
  comprehensive WMO/GRIB2 parameter table. Extending coverage means
  adding real, checked entries to those JSON files, not guessing.
"""

from acf.normalization.normalizer import normalize_variable
from acf.normalization.units import convert_unit
from acf.normalization.variable_names import to_cf_standard_name

__all__ = ["normalize_variable", "convert_unit", "to_cf_standard_name"]
