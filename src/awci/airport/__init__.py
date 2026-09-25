"""AWCI airport operations.

Migrated 2026-09-21 (Phase 8 of the AWCI separate-package migration -
see ``awci``'s own package docstring and
``docs/architecture/acf_awci_architecture_gap_analysis.md``) from
``acf.awci``. Real airport approach/departure corridor geometry - the
blueprint's own ``awci/airport/`` layer, started with its first real
module.

Extended 2026-09-21 with ``runway.py`` (real per-runway-end headwind/
crosswind assessment) and ``weather.py`` (real per-airport weather
snapshot, composing ``awci.observations.hub.ObservationsHub`` with the
already-real ceiling/present-weather classification elsewhere in this
codebase). ``terminal.py``/``operations.py``/``runway_condition.py``/
``departure.py``/``arrival.py``/``disruption.py`` (the blueprint's
remaining named files) are deliberately not built - each would need
either real terminal-infrastructure data this codebase does not have,
or a real, cited regulatory go/no-go threshold (e.g. a per-aircraft-
type maximum demonstrated crosswind) this codebase does not have
either, and fabricating either would be exactly the kind of invented
operational content this whole session's knowledge-base work has
avoided throughout.
"""
