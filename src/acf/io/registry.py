"""
Atmospheric Complexity Framework (ACF)

IO - Registry

Purpose:
--------
I/O framework, reader factories, and data stream management.

Responsibilities:
-----------------
• Manage registry logic and state representations.
• Integrate with the io subsystem of the ACF scientific engine.

Major Components:
-----------------
• ReaderRegistry

Dependencies:
-------------
• Python Standard Library and NumPy/Scientific Python Stack.
• Internal acf.io module infrastructure.

Scientific Context:
-------------------
Provides foundational capabilities for numerical weather prediction, atmospheric data processing,
physical modeling, and spatial-temporal analysis within the Atmospheric Complexity Framework.
"""

class ReaderRegistry:

    def __init__(self):

        self._readers = []

    def register(self, reader):

        self._readers.append(reader)

    def readers(self):

        return list(self._readers)

    def count(self):

        return len(self._readers)
