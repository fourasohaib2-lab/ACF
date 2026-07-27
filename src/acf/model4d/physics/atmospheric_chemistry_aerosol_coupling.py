"""
ACF - Atmospheric Complexity Framework

Atmospheric Chemistry Aerosol Coupling Physics Module

Models simplified interactions between:
- aerosol chemical composition
- particulate matter
- atmospheric chemistry
- cloud interactions
- radiative effects
"""


class AtmosphericChemistryAerosolCouplingPhysics:
    """
    Physics engine for atmospheric chemistry and aerosol coupling.
    """

    MODULE_NAME = "Atmospheric Chemistry Aerosol Coupling Physics"


    @staticmethod
    def pm25_concentration(emission_rate, removal_rate):
        """
        Estimate PM2.5 concentration.

        concentration = emissions - removal
        """

        if emission_rate < 0:
            raise ValueError("Emission rate must be positive")

        if removal_rate < 0:
            raise ValueError("Removal rate must be positive")

        return emission_rate - removal_rate


    @staticmethod
    def pm10_fraction(pm10, pm25):
        """
        Calculate coarse particle fraction.
        """

        if pm10 < 0 or pm25 < 0:
            raise ValueError("Particle concentration must be positive")

        if pm25 > pm10:
            raise ValueError("PM2.5 cannot exceed PM10")

        return pm10 - pm25


    @staticmethod
    def sulfate_aerosol_formation(so2_concentration, oxidation_rate):
        """
        Simplified SO2 oxidation into sulfate aerosols.
        """

        if so2_concentration < 0:
            raise ValueError("SO2 concentration must be positive")

        if oxidation_rate < 0:
            raise ValueError("Oxidation rate must be positive")

        return so2_concentration * oxidation_rate


    @staticmethod
    def black_carbon_radiative_effect(concentration, absorption_efficiency):
        """
        Estimate black carbon warming effect.
        """

        if concentration < 0:
            raise ValueError("Black carbon concentration must be positive")

        if not 0 <= absorption_efficiency <= 1:
            raise ValueError(
                "Absorption efficiency must be between 0 and 1"
            )

        return concentration * absorption_efficiency


    @staticmethod
    def aerosol_cloud_nucleation(aerosol_number, activation_ratio):
        """
        Aerosol influence on cloud condensation nuclei.
        """

        if aerosol_number < 0:
            raise ValueError("Aerosol number must be positive")

        if not 0 <= activation_ratio <= 1:
            raise ValueError(
                "Activation ratio must be between 0 and 1"
            )

        return aerosol_number * activation_ratio


    @staticmethod
    def chemistry_radiative_feedback(
        aerosol_loading,
        radiative_factor
    ):
        """
        Aerosol chemical-radiative feedback.
        """

        return aerosol_loading * radiative_factor


    @staticmethod
    def module_status():
        return {
            "module": AtmosphericChemistryAerosolCouplingPhysics.MODULE_NAME,
            "status": "active",
            "domain": "atmospheric chemistry and aerosols"
        }
