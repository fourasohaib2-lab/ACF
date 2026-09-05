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

UPDATE (2026-09-05, "continue selon ton jugement" - the follow-up
duplication audit this file's own docstring had flagged as separate
future work): 151 real files under `physics/` (not ~150 - counted
directly), not all disconnected for the same reason.

By exact filename, only 15 of 151 collide with a same-named file under
`acf.science`/`acf.simulation_engine`/`acf.earth_physics`; by exact
top-level class name, only 3 (`Divergence`, `Dynamics`, `Moisture`) -
weaker overlap than this docstring's earlier wording implied, though
`dynamics.py`/`moisture.py`'s class bodies differ enough in length
(28 vs. 103, 119 vs. 102 lines) that "duplicate" undersells it as much
as "distinct" would - same physical concept, independently
implemented, at different depth.

More significant finding, NOT about duplication: 21 of these 151 files
are named `*_engine.py` with AI/ML/"intelligence" branding
(`self_improving_forecast_neural_engine.py`,
`global_weather_knowledge_graph_engine.py`,
`weather_causal_reasoning_engine.py`, `natural_language_weather_
intelligence_engine.py`, and 17 more - full list in
`reports/ACF_MASTER_AUDIT_v2.md`'s own model4d section). 7 of the 21
already carry a real Physics Guard correction from an earlier pass
(e.g. `weather_causal_reasoning_engine.py`'s own NOTE, which removed
an unexplained calibration offset). Of the 14 that do NOT yet, this
pass opened and read `self_improving_forecast_neural_engine.py` and
`global_weather_knowledge_graph_engine.py` in full: neither trains,
loads, or runs any actual model, graph structure, or NLP component -
`SelfImprovingForecastNeuralEngine.improvement_gain()` is
`learning_rate * training_cycles`, and
`GlobalWeatherKnowledgeGraphEngine.find_weather_analogue()` is a
linear scan computing `100 - abs-difference/4` against an in-memory
list - real, deterministic Python, but arbitrary weighted-sum/nearest-
neighbour arithmetic wearing a "neural"/"knowledge graph" name, not
the capability the name claims. Only these 2 of the 14 were opened
(not an exhaustive sweep of all 14) - both confirmed the same pattern,
which is what these 2 files' own file names, siblings' names, and
sprint-numbered class docstrings ("Sprint 9.52", "Sprint 9.53" -
matching this whole package's real, git-verified sprint-by-sprint
history) suggest is likely true of some or all of the remaining 12,
but that remains this pass's own honest limitation, not verified here.

Disposition still not decided, and still not this pass's call to make
unilaterally (same reasoning as before: archiving/deleting 179 real,
tested files is a large, hard-to-reverse action). What's different now
is the reason FOR archiving is stronger than "unused" alone - a
meaningful fraction of this reserve is cosmetic/fabricated-sounding
scaffolding, not dormant real physics, which is exactly the pattern
this project's audits exist to flag rather than let sit undocumented
in a reserve someone might resurrect later while trusting its names.
"""
