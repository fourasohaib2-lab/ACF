"""
Atmospheric Complexity Framework
Weather Field
"""


class WeatherField:
    """Represents a meteorological field."""

    def __init__(self, name, values=None, units=""):
        self.name = name
        self.values = values if values is not None else []
        self.units = units

    def minimum(self):
        return min(self.values) if self.values else None

    def maximum(self):
        return max(self.values) if self.values else None

    def mean(self):
        if not self.values:
            return None
        return sum(self.values) / len(self.values)

    def count(self):
        return len(self.values)

    def add(self, value):
        self.values.append(value)

    def clear(self):
        self.values.clear()

    def __repr__(self):
        return f"WeatherField(name={self.name!r}, count={self.count()}, units={self.units!r})"
