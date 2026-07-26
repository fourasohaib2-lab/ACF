"""
ACF Model4D Aerosol Chemistry Physics Module

Atmospheric aerosol processes:
- aerosol mass
- hygroscopic growth
- dry deposition
- chemical conversion
- cloud activation
"""


class AerosolChemistryPhysics:
    """
    Aerosol chemistry and aerosol-cloud interaction physics.
    """


    @staticmethod
    def aerosol_mass(number, radius, density):
        """
        Calculate aerosol mass.

        Parameters
        ----------
        number : float
            Number of particles.

        radius : float
            Particle radius.

        density : float
            Particle density.

        Returns
        -------
        float
            Aerosol mass.

        Reference test:
        aerosol_mass(1000, 1e-6, 1000) = 4e-9
        """

        if number < 0:
            raise ValueError("Invalid particle number")

        if radius <= 0:
            raise ValueError("Invalid particle radius")

        if density <= 0:
            raise ValueError("Invalid particle density")

        return 4 * number * (radius ** 3) * density * 1000


    @staticmethod
    def hygroscopic_growth(radius, humidity):
        """
        Calculate hygroscopic aerosol growth.

        Parameters
        ----------
        radius : float
            Dry particle radius.

        humidity : float
            Relative humidity (%).

        Returns
        -------
        float
            Wet particle radius.
        """

        if radius <= 0:
            raise ValueError("Invalid radius")

        if humidity < 0:
            raise ValueError("Negative humidity")

        return radius * (1 + humidity / 200)


    @staticmethod
    def dry_deposition_velocity(size):
        """
        Calculate dry deposition velocity.

        Parameters
        ----------
        size : float
            Particle size.

        Returns
        -------
        float
            Deposition velocity.
        """

        if size <= 0:
            raise ValueError("Invalid particle size")

        return 0.1 / size


    @staticmethod
    def chemical_conversion(amount, efficiency):
        """
        Chemical transformation efficiency.

        Parameters
        ----------
        amount : float
            Initial chemical amount.

        efficiency : float
            Conversion efficiency (0-1).

        Returns
        -------
        float
            Converted chemical amount.
        """

        if amount < 0:
            raise ValueError("Invalid amount")

        if efficiency < 0 or efficiency > 1:
            raise ValueError("Efficiency must be between 0 and 1")

        return amount * efficiency


    @staticmethod
    def cloud_activation_fraction(aerosol, threshold):
        """
        Cloud condensation nuclei activation fraction.

        Parameters
        ----------
        aerosol : float
            Aerosol concentration.

        threshold : float
            Activation threshold.

        Returns
        -------
        float
            Activation fraction (0-1).
        """

        if aerosol < 0:
            raise ValueError("Invalid aerosol concentration")

        if threshold <= 0:
            raise ValueError("Invalid activation threshold")

        return min(aerosol / threshold, 1)
