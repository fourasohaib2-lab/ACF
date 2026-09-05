"""
Atmospheric Complexity Framework (ACF)

PARAMETERS - Categories

Purpose:
--------
Physical parameter definitions, unit conversion tables, and parameter aliases.

Responsibilities:
-----------------
• Manage categories logic and state representations.
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

NOTE (correction, 2026-09-05 audit de continuation): this module is an
empty scaffolding stub - no category taxonomy exists here despite the
"Categories" purpose claimed above. Not imported by anything in src/ or
tests/ (verified by grep). ParameterRegistry.categories()/by_category()
(acf.parameters.registry) already provide a real, working category
grouping derived directly from each registered Parameter.category
field - this file duplicates neither it nor anything else. Disclosure
only, no behavior to correct.
"""
