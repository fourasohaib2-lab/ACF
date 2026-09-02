"""
ACF Physics Guard — transversal scientific validation infrastructure
========================================================================

Explicit user request: the "Prompt Maître ACF v2.0" master specification's
section 22 describes Physics Guard as infrastructure that must sit in
front of "any scientific operation" (UNIT CHECK -> DIMENSION CHECK ->
RANGE CHECK -> COORDINATE CHECK -> VERTICAL CHECK -> TIME CHECK ->
SCIENTIFIC CONSISTENCY), and reports/ACF_MASTER_AUDIT_v2.md found this
genuinely absent from the codebase - not a duplicate of the "Physics
Guard" AUDIT METHODOLOGY already applied throughout this project's
history (docs/ACF_PHYSICS_GUARD_AUDIT_CHANGELOG.md), which is a different
thing (a review discipline for catching fabricated data, applied by a
human/Claude during development) from this package (runtime validation
code a caller can invoke on real data).

What's built here (real, tested, reusing existing infrastructure)
-----------------------------------------------------------------
- unit_check: real dimensional-compatibility checking via
  acf.normalization.units (MetPy/pint) - not a hand-rolled table.
- range_check: ACF's own documented operational sanity bounds (NOT a
  claim of the absolute physical limits of the atmosphere anywhere -
  see range_check.py's own disclosure) for the variables
  acf.normalization.variable_names already has real CF entries for.
- coordinate_check: real lat/lon range validation - directly motivated
  by two real bugs this project found and fixed this session (a
  swapped lons/lats assignment that crashed matplotlib, caught by a
  test using a deliberately non-square grid - see
  gui/dashboard/awci_dashboard.py's git history). A PhysicsGuard
  coordinate check would have caught that exact bug class immediately,
  which is why this check exists.
- vertical_check: real monotonicity check (pressure must decrease with
  altitude) - the same physical invariant already verified with real
  solver output in acf.awci.vertical_field's own tests
  (test_pressure_decreases_with_altitude_real_physics), generalized
  into reusable validation code instead of staying a one-off test
  assertion.
- time_check: forecast time ordering (valid_time >= forecast_reference_time).
- consistency_check: real cross-variable physical relationships (dew
  point cannot exceed air temperature; relative humidity must stay in
  [0, 100]%).
- PhysicsGuard: orchestrates whichever checks apply to a given payload
  into one real validation pass, collecting every violation found (not
  stopping at the first) into a PhysicsGuardReport.

Honest scope
-------------
Not every check in the master spec's pipeline diagram is built:
DIMENSION CHECK here only covers the specific case of coordinate-array/
field-shape mismatches for the arrays ACF's own real 2D/3D/4D fields
already use (acf.awci.spatial_field/vertical_field/temporal_field) -
not a fully generic dimensional-analysis engine for arbitrary tensors.
"""

from acf.physics_guard.guard import PhysicsGuard, PhysicsGuardReport

__all__ = ["PhysicsGuard", "PhysicsGuardReport"]
