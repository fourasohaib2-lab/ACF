"""
Atmospheric Complexity Framework (ACF)

CORE - Parameter

Purpose:
--------
Core application lifecycle, service management, plugin registry, and base configurations.

Responsibilities:
-----------------
• Manage parameter logic and state representations.
• Integrate with the core subsystem of the ACF scientific engine.

Major Components:
-----------------
• Parameter

Dependencies:
-------------
• Python Standard Library and NumPy/Scientific Python Stack.
• Internal acf.core module infrastructure.

Scientific Context:
-------------------
Provides foundational capabilities for numerical weather prediction, atmospheric data processing,
physical modeling, and spatial-temporal analysis within the Atmospheric Complexity Framework.
"""

from dataclasses import dataclass, field


@dataclass(slots=True)
class Parameter:

    id: str

    name: str

    units: str

    category: str

    renderer: str

    colormap: str

    description: str = ""

    alert_levels: dict = field(default_factory=dict)
