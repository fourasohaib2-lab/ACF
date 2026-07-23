"""
Storm Motion
============
"""


class StormMotion:
    """Simple storm motion calculator."""

    @staticmethod
    def calculate(
        mean_u: float,
        mean_v: float,
        deviation_u: float = 7.5,
        deviation_v: float = 7.5,
    ) -> tuple[float, float]:
        """
        Approximate Bunkers storm motion.
        """

        storm_u = mean_u + deviation_u
        storm_v = mean_v + deviation_v

        return storm_u, storm_v
