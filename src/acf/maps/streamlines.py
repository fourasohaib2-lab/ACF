"""
Atmospheric Complexity Framework (ACF)
Streamlines Engine
==============================
"""


class Streamlines:
    """Manage streamline fields."""

    def __init__(self):
        self._streamlines = {}

    def add(self, name: str, u, v):
        """Add a streamline field."""
        self._streamlines[name] = {
            "u": u,
            "v": v,
        }

    def get(self, name: str):
        """Return a streamline field."""
        return self._streamlines.get(name)

    def exists(self, name: str):
        """Check if a field exists."""
        return name in self._streamlines

    def remove(self, name: str):
        """Remove a streamline field."""
        self._streamlines.pop(name, None)

    def clear(self):
        """Remove all streamline fields."""
        self._streamlines.clear()

    def count(self):
        """Return the number of fields."""
        return len(self._streamlines)

    def names(self):
        """Return all field names."""
        return sorted(self._streamlines.keys())

    def __repr__(self):
        return f"Streamlines(fields={len(self._streamlines)})"
