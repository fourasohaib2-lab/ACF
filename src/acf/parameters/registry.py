"""
Parameter Registry (Canonical Implementation)
"""

from acf.parameters.parameter import Parameter


class ParameterRegistry:

    def __init__(self):
        self._parameters = {}
        self.parameters = self._parameters

    def register(self, parameter: Parameter):
        key = parameter.code or parameter.id
        self._parameters[key] = parameter

    def unregister(self, code):
        self._parameters.pop(code, None)

    def exists(self, code):
        return code in self._parameters

    def get(self, code):
        return self._parameters.get(code)

    def list_codes(self):
        return sorted(self._parameters.keys())

    def count(self):
        return len(self._parameters)

    def clear(self):
        self._parameters.clear()

    def all(self):
        return list(self._parameters.values())

    def categories(self):
        return sorted(
            {
                p.category
                for p in self._parameters.values()
                if hasattr(p, "category") and p.category
            }
        )

    def by_category(self, category):
        return [
            p
            for p in self._parameters.values()
            if getattr(p, "category", None) == category
        ]
