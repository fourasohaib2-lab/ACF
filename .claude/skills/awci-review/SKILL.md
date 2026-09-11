---
name: awci-review
description: Review checklist for any change touching acf.awci or acf.gui.dashboard.awci_* (calculator modules, path_sampling, map panels, dashboard wiring). Use before finishing a task that adds or modifies AWCI code, or when the user asks to review/audit an AWCI change. Enforces this repo's own established scientific-integrity conventions — real formula vs. disclosed proxy vs. forbidden fabrication, unit consistency, PhysicsGuard usage, regression tests, and doc sync.
---

# AWCI review checklist

This project (`ACF`/`AWCI`) has an explicit, repeatedly-enforced convention
across its own commit history and docstrings: **real formula, disclosed
proxy where no real one exists yet, never a fabricated number presented as
real.** This skill formalizes the checks already applied manually
throughout `src/acf/awci/` and `src/acf/gui/dashboard/awci_*.py` — run it
before considering any AWCI change finished.

## 1. Real vs. proxy vs. fabrication

For every new or changed numeric output, answer explicitly:

- **Is this a real physical formula from a named, reputable source?**
  (a textbook equation, a peer-reviewed reference — e.g.
  `acf.science.wind_turbulence.CATIndex` cites Ellrod & Knapp 1992). If
  yes, cite the source in the docstring, the way existing modules already
  do.
- **Is a real formula not available for what's genuinely needed?** Use a
  disclosed proxy — a real quantity that correlates with what's wanted,
  explicitly labeled as a proxy in the docstring and never presented as
  the thing itself (e.g. `acf.awci.wind_shear`'s bulk shear standing in
  for a full CAT index before this session's closure).
- **Never**: a hardcoded/guessed constant presented as a real computed
  result (the `"FL360"` stubs and the `earth_system_operations.py`
  self-certification found and gutted earlier in this project's own
  history are the cautionary examples — search `docs/STATUS.md` for
  "auto-certification fabriquée" for the full story). If the only way to
  produce a number is to invent it, don't build the feature — document it
  in `docs/awci/future-improvements.md` instead, with a real, specific
  "what would make this real" note.

## 2. Units

AWCI has a documented history of real unit-mismatch bugs (hPa vs Pa
between `AWCICalculator` and CF-canonical units, see
`AWCI_IMPLEMENTATION_STATUS.md`'s "Bugs found and fixed"). For any new
formula wiring:

- Trace every input's real unit back to its source (a solver field's own
  docstring, `acf.normalization`'s CF canonical unit, or a science
  module's own docstring) — never assume.
- If a formula's expected units differ from what's available (e.g.
  `CATIndex.vertical_wind_shear` wants s⁻¹, a bulk shear helper gives
  m/s), do the real conversion (a real height difference, e.g. via
  `acf.science.hypsometric_equation.HypsometricEquation`) rather than
  passing the wrong-unit value through silently.
- State the resulting unit explicitly in the docstring, including
  disclosed conventions this codebase already uses loosely (e.g.
  "per grid step" horizontal gradients, not per physical distance,
  because no per-point map projection exists here yet).

## 3. Reuse before reinventing

Grep for an existing formula/module before writing a new one — this
codebase's own history repeatedly finds "real formula, never wired in"
gaps (`acf.awci.convective_energy`'s own docstring is the canonical
example) rather than missing formulas. Check `src/acf/science/` and
`src/acf/awci/` first.

## 4. PhysicsGuard

If the new/changed function accepts real physical inputs with plausible
range bounds, check whether an opt-in `validate_physics: bool = False`
parameter (the established pattern, e.g. `acf.awci.wind_shear`,
`acf.awci.theta_e`) should be added — off by default, zero behavior
change unless requested.

## 5. Tests

- A new real formula needs a regression test that recomputes the expected
  value independently (not just "doesn't crash" or "returns the right
  shape") — see `tests/test_awci_path_sampling.py`'s
  `*_matches_a_direct_*_call` naming convention.
- A demo-mode vs. Real-Physics-mode asymmetry (common in this codebase)
  needs its own explicit test on each side — never assume one mode's test
  covers the other.
- Run the relevant `tests/test_awci_*.py` files (and `tests/gui/` ones
  touching the same dashboard, when a GUI-capable environment is
  available) before considering the change done.

## 6. Documentation sync

Real, non-trivial AWCI changes get disclosed, not silently shipped. Check
whether these need an update:

- `docs/awci/future-improvements.md` — if this closes or narrows a
  previously-disclosed gap.
- `docs/awci/AWCI_IMPLEMENTATION_STATUS.md` — its "What was NOT built"
  list.
- `docs/STATUS.md` — only if the change affects the audit status of a
  whole module (Tier F/C/E), not for routine AWCI closures.
- The function/class docstring itself — this codebase's convention is
  docstrings that explain the *real* scope and honest limitations, not
  just parameters/returns.

## 7. Lint/type clean

`ruff check` and `mypy` (project config, see `pyproject.toml`) on every
touched file — this project keeps both clean on every closure.
