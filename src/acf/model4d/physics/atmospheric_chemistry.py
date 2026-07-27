"""
Atmospheric Chemistry Physics Module
Atmospheric Complexity Framework (ACF)

Core atmospheric chemical processes:
- ozone chemistry
- reaction rates
- photolysis
- chemical lifetimes
- mixing ratios
- pollutant concentration conversion
"""


import math


class AtmosphericChemistryPhysics:
    """
    Atmospheric chemistry calculations.
    """

    @staticmethod
    def reaction_rate(k, concentration_a, concentration_b):
        """
        Second order chemical reaction rate.

        Rate = k[A][B]
        """

        return k * concentration_a * concentration_b


    @staticmethod
    def ozone_production(nox, voc):
        """
        Simplified ozone production index.

        O3 production proportional to NOx and VOC.
        """

        return nox * voc * 1.5


    @staticmethod
    def photolysis_rate(j_value, concentration):
        """
        Photolysis loss rate.

        Loss = J * concentration
        """

        return j_value * concentration


    @staticmethod
    def chemical_lifetime(concentration, loss_rate):
        """
        Chemical lifetime.

        tau = concentration / loss rate
        """

        return concentration / loss_rate


    @staticmethod
    def mixing_ratio_concentration(
        concentration,
        air_density
    ):
        """
        Convert concentration to mixing ratio.

        Simplified ppm representation.
        """

        return concentration / air_density * 1e6


    @staticmethod
    def exponential_decay(initial,
                          lifetime,
                          time):
        """
        Chemical exponential decay.

        C(t)=C0 exp(-t/tau)
        """

        return initial * math.exp(
            -time / lifetime
        )


    @staticmethod
    def methane_lifetime(
        methane,
        oxidation_loss
    ):
        """
        Methane lifetime.

        tau = CH4 / loss
        """

        return methane / oxidation_loss


    @staticmethod
    def ozone_column_density(
        concentration,
        height
    ):
        """
        Column ozone approximation.

        DU simplified representation.
        """

        return concentration * height * 1e-3


    @staticmethod
    def arrhenius_rate(
        activation_energy,
        temperature
    ):
        """
        Arrhenius simplified rate.

        k = exp(-Ea/(R*T))
        """

        R = 8.314

        return math.exp(
            -activation_energy /
            (R * temperature)
        )


    @staticmethod
    def aerosol_effect(
        aerosol,
        radiation
    ):
        """
        Aerosol radiative chemistry interaction.
        """

        return aerosol * radiation
