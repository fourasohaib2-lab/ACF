"""
Color Table
===========
"""


class ColorTable:

    def __init__(self):

        self._table = {}

    def add(self, variable, colormap):

        self._table[variable] = colormap

    def get(self, variable):

        return self._table.get(variable)

    def remove(self, variable):

        self._table.pop(variable, None)

    def exists(self, variable):

        return variable in self._table

    def variables(self):

        return sorted(self._table.keys())

    def count(self):

        return len(self._table)

    def clear(self):

        self._table.clear()

    def __repr__(self):

        return f"ColorTable(count={self.count()})"

