"""
Projection Manager
==================
"""


class ProjectionManager:
    def __init__(self):
        self._projections = {}
        self._default = None

    def add(self, name, projection):
        self._projections[name] = projection

        if self._default is None:
            self._default = name

    def get(self, name):
        return self._projections.get(name)

    def remove(self, name):
        self._projections.pop(name, None)

        if self._default == name:
            self._default = None

    def exists(self, name):
        return name in self._projections

    def names(self):
        return list(self._projections.keys())

    def count(self):
        return len(self._projections)

    def set_default(self, name):
        if name in self._projections:
            self._default = name

    def default(self):
        if self._default is None:
            return None

        return self._projections[self._default]

    def default_name(self):
        return self._default

    def clear(self):
        self._projections.clear()
        self._default = None

    def __repr__(self):
        return f"ProjectionManager(count={len(self._projections)})"
