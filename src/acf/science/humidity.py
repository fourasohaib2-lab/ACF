class Humidity:

    @staticmethod
    def clip(value):

        return max(0.0, min(100.0, value))
