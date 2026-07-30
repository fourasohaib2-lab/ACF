"""
Atmospheric Complexity Framework (ACF)

IO - Manager

Purpose:
--------
I/O framework, reader factories, and data stream management.

Responsibilities:
-----------------
• Manage manager logic and state representations.
• Integrate with the io subsystem of the ACF scientific engine.

Major Components:
-----------------
• DataManager

Dependencies:
-------------
• Python Standard Library and NumPy/Scientific Python Stack.
• Internal acf.io module infrastructure.

Scientific Context:
-------------------
Provides foundational capabilities for numerical weather prediction, atmospheric data processing,
physical modeling, and spatial-temporal analysis within the Atmospheric Complexity Framework.
"""

from acf.io.factory import ReaderFactory


class DataManager:

    def __init__(self, registry):

        self.factory = ReaderFactory(registry)

    def open(self, filename):

        reader = self.factory.get_reader(filename)

        if reader is None:
            raise ValueError(f"No reader available for {filename}")

        return reader.read(filename)
