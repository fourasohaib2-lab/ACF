import math


class Wind:

    @staticmethod
    def speed(u, v):

        return math.sqrt(u**2 + v**2)
