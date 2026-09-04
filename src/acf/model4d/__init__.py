"""
Atmospheric Complexity Framework (ACF)

MODEL4D -   Init

Purpose:
--------
4D spatio-temporal grid mechanics, field representations, differential operators, and physical parameterizations.

Responsibilities:
-----------------
• Manage   init   logic and state representations.
• Integrate with the model4d subsystem of the ACF scientific engine.

Major Components:
-----------------
• Module functions and constants

Dependencies:
-------------
• Python Standard Library and NumPy/Scientific Python Stack.
• Internal acf.model4d module infrastructure.

Scientific Context:
-------------------
Provides foundational capabilities for numerical weather prediction, atmospheric data processing,
physical modeling, and spatial-temporal analysis within the Atmospheric Complexity Framework.

NOTE (investigation, 2026-09-05): this package is real and has real,
already-passing test coverage (169 test files under tests/ import
from acf.model4d, part of the project's own full green suite) - it is
NOT broken or abandoned code. It IS, however, completely disconnected
from the rest of ACF: an exhaustive `grep -rl "from acf.model4d"`
across every other package in `src/acf/` returns zero results.
`ModuleRegistry` never references it, no ESOC panel uses it, and the
ACF Scientific Workstation doesn't touch it.

Git history shows this package existed from the project's very first
commit ("Initial commit - ACF Foundation v0.1", 2026-07-21) and was
built out sprint-by-sprint (commit messages: "Sprint 6.5 terminé -
CubicInterpolation", "Sprint 6.4 terminé - TrilinearInterpolation",
etc.) - a deliberate early architecture, not an accidental orphan.
`docs/ACF_MASTER_PROMPT.md` sections 23/50 explicitly call for a real
`C(x,y,z,t)`/`AWCI(x,y,z,t)` 4D capability ("Volume + temps... naviguer
longitude/latitude/altitude/temps") - this package looks like an
early attempt at exactly that requirement.

That same master-prompt requirement is now satisfied a DIFFERENT real
way: `acf.awci.vertical_field.compute_real_complexity_volume()` (x,y,z)
+ `acf.awci.temporal_field.compute_real_complexity_evolution()` (+t) +
the ACF Scientific Workstation's own level slider/Domain selector/
Global Timeline (Phase 41, 2026-09-05) together deliver a real,
tested, already-shipped 4D navigation capability - built later, and
apparently superseding this package's own approach rather than
replacing it outright (this package was never deleted, matching this
project's own "never delete real capability" convention).

Spot-checked for redundancy: `acf.model4d.operators.divergence.
Divergence` and `acf.science.divergence.Divergence` (the one actually
used throughout the shipped codebase, e.g. by
`acf.awci.workstation_fields.compute_real_vorticity_divergence`) are
near-identical in formula and even share the same class name -
evidence this package substantially duplicates functionality that
already exists, tested, and integrated elsewhere under different
package names (`acf.science`/`acf.simulation_engine`/`acf.earth_physics`).

Not yet resolved: whether every one of the ~150 physics files here
duplicates its `acf.science`/`acf.simulation_engine`/`acf.earth_physics`
counterpart this precisely, or whether some carry genuinely distinct
real capability worth salvaging. Left as a real, disclosed, low-
priority reserve rather than integrated or removed - a full
duplication audit (or a decision to retire/archive it) is real,
separate future work.
"""
