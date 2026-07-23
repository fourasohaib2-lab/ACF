import math


class DewPoint:

    @staticmethod
    def calculate(temperature_c, relative_humidity):

        a = 17.27
        b = 237.7

        gamma = (
            (a * temperature_c) / (b + temperature_c)
            + math.log(relative_humidity / 100.0)
        )

        return (b * gamma) / (a - gamma)
