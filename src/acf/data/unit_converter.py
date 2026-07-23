"""
Universal Unit Converter
"""


class UnitConverter:

    def convert(self, value, source, target):

        if source == target:
            return value

        # Temperature
        if source == "K" and target == "°C":
            return value - 273.15

        if source == "°C" and target == "K":
            return value + 273.15

        # Pressure
        if source == "Pa" and target == "hPa":
            return value / 100.0

        if source == "hPa" and target == "Pa":
            return value * 100.0

        # Wind
        if source == "m s-1" and target == "km h-1":
            return value * 3.6

        if source == "km h-1" and target == "m s-1":
            return value / 3.6

        # Rain
        if source == "mm" and target == "m":
            return value / 1000.0

        if source == "m" and target == "mm":
            return value * 1000.0

        raise ValueError(
            f"Unsupported conversion : {source} -> {target}"
        )
