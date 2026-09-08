"""
Atmospheric Complexity Framework (ACF)

GUI -   Init

Purpose:
--------
PySide6 Qt GUI components, dock panels, map canvas controllers, and navigation.

Responsibilities:
-----------------
• Manage   init   logic and state representations.
• Integrate with the gui subsystem of the ACF scientific engine.

Major Components:
-----------------
• Module functions and constants

Dependencies:
-------------
• Python Standard Library and NumPy/Scientific Python Stack.
• Internal acf.gui module infrastructure.

Scientific Context:
-------------------
Provides foundational capabilities for numerical weather prediction, atmospheric data processing,
physical modeling, and spatial-temporal analysis within the Atmospheric Complexity Framework.
"""


# NOTE (found, NOT changed — RÈGLE D'OR / single source of truth): every
# class in this subpackage is unused by anything in src/ - see
# acf/gui/map/__init__.py's own NOTE for the full explanation (this is
# part of a complete, correct, but never-integrated alternate map
# architecture superseded in practice by the flat map_canvas.py/
# map_layers.py/map_projection.py/map_renderer.py files that ESOC
# actually uses).
