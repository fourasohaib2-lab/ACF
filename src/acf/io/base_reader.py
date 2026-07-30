"""
Atmospheric Complexity Framework (ACF)

IO - Base Reader

Purpose:
--------
I/O framework, reader factories, and data stream management.

Responsibilities:
-----------------
• Manage base reader logic and state representations.
• Integrate with the io subsystem of the ACF scientific engine.

Major Components:
-----------------
• BaseReader

Dependencies:
-------------
• Python Standard Library and NumPy/Scientific Python Stack.
• Internal acf.io module infrastructure.

Scientific Context:
-------------------
Provides foundational capabilities for numerical weather prediction, atmospheric data processing,
physical modeling, and spatial-temporal analysis within the Atmospheric Complexity Framework.
"""

from abc import ABC, abstractmethod


class BaseReader(ABC):

    extensions = []

    @abstractmethod
    def can_read(self, filename: str) -> bool:
        pass

    @abstractmethod
    def read(self, filename: str):
        pass
