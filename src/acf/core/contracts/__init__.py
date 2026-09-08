"""
ACF Data Contract
====================

Explicit user request: the "Prompt Maître ACF v2.0" master specification's
sections 4, 13 and 14 describe a formal Data Contract (a `Dataset`
carrying real values plus complete metadata) and a Scientific Variable
Contract - reports/ACF_MASTER_AUDIT_v2.md found neither existed as a
formal, constructible type anywhere in the codebase (only informal,
partial equivalents scattered across acf.science.encyclopedia.entry.
EncyclopediaEntry and the ad hoc dicts acf.awci.spatial_field/
vertical_field/temporal_field already return).

What's built here
--------------------
- Dataset: the §13 contract (id, source, model, run,
  forecast_reference_time, valid_time, lead_time, variable, unit,
  dimensions, coordinates, horizontal_grid, vertical_coordinate,
  ensemble_member, quality, uncertainty, provenance, version), plus the
  real array of values it describes (not in the original field list,
  but a metadata contract with nothing to validate against is not
  useful - see the class's own docstring).
- VariableContract: the §14 Scientific Variable Contract
  (name, standard_name, unit, dimensions, valid_range, description,
  source_variables, derivation, references, uncertainty,
  quality_requirements), with a real from_registry() that builds one
  from ACF's own already-real reference tables
  (acf.normalization.variable_names + acf.physics_guard.range_check) -
  not invented values.
- Provenance, QualityInfo, UncertaintyInfo: the smaller contracts
  Dataset embeds.

Dataset.validate() reuses acf.physics_guard.PhysicsGuard (not a second,
parallel validation implementation) - this is the actual "ACF 4D DATA
MODEL -> PHYSICS GUARD" link the master spec's architecture diagram
(section 3/39) describes.

Dataset.from_real_field()/from_real_volume() bridge this contract to
the REAL, already-working outputs of acf.awci.spatial_field.
compute_real_complexity_field() and acf.awci.vertical_field.
compute_real_complexity_volume() - proving the contract is usable on
real ACF data, not a type nothing in the codebase ever constructs.

Honest scope: this Dataset does not yet replace or wrap the ad hoc dict
shapes acf.awci's own field/volume/evolution functions return -
building it is this session's first step; migrating those call sites to
construct real Dataset instances (rather than plain dicts) is a
separate, larger, deliberately NOT-done-in-one-pass change (see the
Prompt Maître's own "travailler par lots contrôlés" instruction).
"""

from acf.core.contracts.dataset import Dataset
from acf.core.contracts.provenance import Provenance
from acf.core.contracts.quality import QualityInfo
from acf.core.contracts.uncertainty import UncertaintyInfo
from acf.core.contracts.variable import VariableContract

__all__ = ["Dataset", "Provenance", "QualityInfo", "UncertaintyInfo", "VariableContract"]
