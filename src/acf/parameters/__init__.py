"""
Atmospheric Complexity Framework (ACF)

PARAMETERS -   Init

Purpose:
--------
Physical parameter definitions, unit conversion tables, and parameter aliases.

Responsibilities:
-----------------
• Manage   init   logic and state representations.
• Integrate with the parameters subsystem of the ACF scientific engine.

Major Components:
-----------------
• Module functions and constants

Dependencies:
-------------
• Python Standard Library and NumPy/Scientific Python Stack.
• Internal acf.parameters module infrastructure.

Scientific Context:
-------------------
Provides foundational capabilities for numerical weather prediction, atmospheric data processing,
physical modeling, and spatial-temporal analysis within the Atmospheric Complexity Framework.

NOTE (correction, 2026-09-05 audit de continuation): the "unit
conversion tables" and "parameter aliases" named in this package's own
Purpose statement above are only partially real. `parameter.py`/
`registry.py`/`hub.py`/`search.py`/`index.py`/`aliases.py`/`catalog.py`
are genuine, tested, actively-used infrastructure (this is the real
canonical Parameter/ParameterRegistry consolidation target from the
ACF-017 duplicate-components audit - see
`acf.core.parameter_registry`/`acf.core.parameter`'s own compatibility-
layer docstrings and `tests/test_collisions_consolidation.py`).
`converter.py`/`validator.py`/`units.py`/`categories.py`, however, are
empty scaffolding stubs with no code at all (see each file's own NOTE)
- no unit-conversion table exists in this package (the real ones are
`acf.data.unit_converter` and `acf.normalization.units`).
"""
