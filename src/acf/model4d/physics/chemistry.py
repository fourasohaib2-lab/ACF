"""
ACF - Atmospheric Complexity Framework
Model4D Physics Module

Chemistry Physics Module

Provides simplified atmospheric chemistry
calculations for trace gases and reactions.
"""



class Chemistry:
    """
    Atmospheric chemistry physical processes.
    """

    @staticmethod
    def mixing_ratio(concentration, air_density):
        """
        Compute mixing ratio.

        Parameters
        ----------
        concentration : float
            Species concentration.
        air_density : float
            Air density.

        Returns
        -------
        float
            Mixing ratio.
        """
        if air_density <= 0:
            raise ValueError("Air density must be positive")

        return concentration / air_density


    @staticmethod
    def reaction_rate(k, concentration_a, concentration_b):
        """
        Compute second-order chemical reaction rate.

        Rate = k[A][B]
        """
        if k < 0:
            raise ValueError("Reaction constant must be positive")

        return k * concentration_a * concentration_b


    @staticmethod
    def photolysis_rate(j, concentration):
        """
        Photochemical loss.

        Loss = J * concentration
        """
        if j < 0:
            raise ValueError("Photolysis coefficient must be positive")

        return j * concentration


    @staticmethod
    def ozone_production(no, o3, sunlight):
        """
        Simplified ozone production index.

        Represents NO + sunlight interactions.
        """
        if sunlight < 0:
            raise ValueError("Sunlight must be positive")

        return no * sunlight * 1e-6


    @staticmethod
    def lifetime(concentration, loss_rate):
        """
        Chemical lifetime.

        tau = concentration / loss_rate
        """
        if loss_rate <= 0:
            raise ValueError("Loss rate must be positive")

        return concentration / loss_rate
