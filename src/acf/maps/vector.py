"""
Atmospheric Complexity Framework (ACF)
Vector Engine
=====================================

Management of vector fields (wind, currents, etc.).
"""


class Vector:
    """Store vector fields."""

    def __init__(self):
        self._vectors = {}

    def add(self, name: str, u, v):
        """Add a vector field."""
        self._vectors[name] = {
            "u": u,
            "v": v,
        }

    def get(self, name: str):
        """Return a vector field."""
        return self._vectors.get(name)

    def exists(self, name: str):
        """Check whether a vector field exists."""
        return name in self._vectors

    def remove(self, name: str):
        """Remove a vector field."""
        self._vectors.pop(name, None)

    def clear(self):
        """Remove all vector fields."""
        self._vectors.clear()

    def count(self):
        """Return the number of vector fields."""
        return len(self._vectors)

    def names(self):
        """Return vector field names."""
        return sorted(self._vectors.keys())

    def __repr__(self):
        return f"Vector(fields={len(self._vectors)})"
