"""
Atmospheric Complexity Framework (ACF)

IO - Factory

Purpose:
--------
I/O framework, reader factories, and data stream management.

Responsibilities:
-----------------
• Manage factory logic and state representations.
• Integrate with the io subsystem of the ACF scientific engine.

Major Components:
-----------------
• ReaderFactory

Dependencies:
-------------
• Python Standard Library and NumPy/Scientific Python Stack.
• Internal acf.io module infrastructure.

Scientific Context:
-------------------
Provides foundational capabilities for numerical weather prediction, atmospheric data processing,
physical modeling, and spatial-temporal analysis within the Atmospheric Complexity Framework.
"""

class ReaderFactory:

    def __init__(self, registry):

        self.registry = registry

    def get_reader(self, filename):

        for reader in self.registry.readers():

            if reader.can_read(filename):
                return reader

        return None
