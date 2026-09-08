# Golden datasets

Real, checked-in reference input/output pairs for genuinely
deterministic ACF computations - the Prompt Maître ACF v2.0's section
31-32 "Golden Datasets" contract. Loaded and compared via
`acf.testing.golden` (`assert_matches_golden()`); the actual regression
tests live in `tests/scientific/regression/test_golden_datasets.py`.

## What qualifies for a golden dataset here, and what does not

Only a computation that is **actually, provably deterministic** gets a
golden file - snapshotting something that is not would make a golden
"regression" test flaky by construction, or worse, quietly re-baseline
itself every run and stop protecting anything.

Deliberately **not** included: a full `CoupledEarthSolver` run.
`ModelConsensusEngine.compute_real_multi_model_disagreement()`'s own
test (`test_compute_real_multi_model_disagreement_seed_is_deterministic_per_point`)
already documents a real, pre-existing reason why - the atmosphere/
ocean solver components call `np.random.*` directly against the
global, unseeded NumPy RNG state, so two runs in the same process can
genuinely differ by a small amount depending on how much global RNG
state earlier code already consumed. A golden file for that would
either be flaky or would need a change to the solver's RNG handling
that is out of scope here - not something to paper over with a loose
tolerance.

## Fixtures

- `isa_standard_atmosphere.json` - `acf.science.encyclopedia.aerodynamics.
  isa_atmosphere.calculate_isa_temperature()`/`calculate_isa_pressure()`
  at 9 standard altitudes. Already independently verified against the
  published ICAO Doc 7488 / ISO 2533:1975 table to within 0.05% (see
  that module's own docstring) - this golden file locks the real
  values so a future accidental change to the formula or its constants
  is caught.
- `awci_calculator_reference_case.json` - one fixed, realistic
  meteorological input through `acf.awci.calculator.AWCICalculator.
  calculate()` (a pure function of its input dict - no RNG, no solver
  stepping) - the full real output (module scores, decomposition,
  level, physical/forecast split).
- `nwp_verification_metrics_reference_case.json` - a small
  `acf.verification.nwp_metrics.NWPVerificationMetrics.evaluate_all()`
  case chosen so bias/mae/rmse/pod/far/csi/ets are exactly
  hand-computable (see the fixture's own `description` field) - not
  just re-derived from the same code that produced it.

## Updating a fixture

Never done automatically by a failing test. If a fixture's expected
value has genuinely, deliberately changed (e.g. a real bug in the
underlying formula was fixed), regenerate it explicitly:

```python
from acf.testing.golden import write_golden
write_golden("some_fixture.json", {...})
```

...and explain why in the commit that changes it, the same as any
other reviewed change to expected test behaviour.
