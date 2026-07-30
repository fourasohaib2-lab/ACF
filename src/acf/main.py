"""
Atmospheric Complexity Framework (ACF)

CORE - Main

Purpose:
--------
Core application lifecycle, service management, plugin registry, and base configurations.

Responsibilities:
-----------------
• Manage main logic and state representations.
• Integrate with the core subsystem of the ACF scientific engine.

Major Components:
-----------------
• Module functions and constants

Dependencies:
-------------
• Python Standard Library and NumPy/Scientific Python Stack.
• Internal acf.core module infrastructure.

Scientific Context:
-------------------
Provides foundational capabilities for numerical weather prediction, atmospheric data processing,
physical modeling, and spatial-temporal analysis within the Atmospheric Complexity Framework.
"""

from acf.gui.app import run

if __name__ == "__main__":
    run()
