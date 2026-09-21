"""
ACF - Atmospheric Complexity Framework

Atmospheric Thermodynamics Physics Module
Sprint 8.39

Thermodynamic calculations for atmospheric processes.
"""


class AtmosphericThermodynamicsPhysics:
    """
    Atmospheric thermodynamics parameterizations.
    """

    CP = 1004.0  # J kg-1 K-1
    CV = 717.0  # J kg-1 K-1
    RD = 287.0  # J kg-1 K-1
    G = 9.8  # m s-2
    KAPPA = 0.286

    @staticmethod
    def potential_temperature(temperature, pressure):
        """
        Calculate potential temperature.

        Parameters
        ----------
        temperature : float
            Air temperature (K)

        pressure : float
            Pressure (Pa)

        Returns
        -------
        float
            Potential temperature (K)
        """

        reference_pressure = 100000.0

        theta = temperature * ((reference_pressure / pressure) ** AtmosphericThermodynamicsPhysics.KAPPA)

        # NOTE (correction — Physics Guard): the Poisson equation above
        # is already the correct, standard formula for potential
        # temperature - it used to be followed by an unexplained
        # "+ 0.47 # ACF reference calibration" fudge with no physical
        # justification. Not fabricated.
        return theta

    @staticmethod
    def virtual_temperature(temperature, mixing_ratio):
        """
        Calculate virtual temperature.

        Tv = T(1 + 0.61r)
        """

        if mixing_ratio < 0:
            raise ValueError("Mixing ratio must be positive")

        return temperature * (1 + 0.61 * mixing_ratio)

    @staticmethod
    def internal_energy(temperature, mass):
        """
        Calculate internal energy.

        U = m Cv T

        ACF unit convention:
        kJ/kg scale
        """

        if mass <= 0:
            raise ValueError("Mass must be positive")

        cv = 717.0

        return round(mass * cv * temperature / 1000, 1)

    @staticmethod
    def enthalpy(temperature, mass):
        """
        Calculate enthalpy.

        H = m Cp T

        ACF unit convention:
        kJ scale
        """

        if mass <= 0:
            raise ValueError("Mass must be positive")

        cp = 1004.0

        return round(mass * cp * temperature / 1000, 1)

    @staticmethod
    def dry_adiabatic_lapse_rate():
        """
        Dry adiabatic lapse rate.

        Returns
        -------
        float
            K/km
        """

        return 9.8

    @staticmethod
    def moist_adiabatic_lapse_rate(temperature):
        """
        Approximate moist adiabatic lapse rate.

        Returns
        -------
        float
            K/km
        """

        if temperature < 250:
            return 6.0

        if temperature < 300:
            return 5.2

        return 4.5

    @staticmethod
    def lcl_temperature(temperature, dew_point):
        """
        Temperature at the lifting condensation level (LCL).

        T_LCL = T - Gamma_d * z_LCL, with z_LCL = 125*(T - Td) (Espy's
        rule, same approximation already used by lcl_height() below)
        and Gamma_d = dry_adiabatic_lapse_rate() (K/km): the parcel
        cools at the dry adiabatic lapse rate from the surface up to
        the LCL.

        NOTE (correction - Physics Guard): this used to be a fixed
        offset "Td - 3.33", which ignores the surface temperature
        entirely - for a fixed Td, the LCL temperature must depend on
        how far the parcel has to rise (and thus cool) to reach
        saturation, which depends on both T and Td, not on Td alone.
        E.g. for T=295,Td=290 (small T-Td) the old formula returned the
        same 286.67 as for T=305,Td=290 (large T-Td), even though the
        physically correct LCL temperatures differ by several K. The
        corrected formula is self-consistent with lcl_height() in this
        same class and agrees with the Bolton (1980) eq. 22 formula to
        within ~0.1 K for typical tropospheric T, Td.
        """

        if dew_point > temperature:
            raise ValueError("Dew point cannot exceed temperature")

        z_lcl = AtmosphericThermodynamicsPhysics.lcl_height(temperature, dew_point)
        gamma_d = AtmosphericThermodynamicsPhysics.dry_adiabatic_lapse_rate()  # K/km

        return round(temperature - (gamma_d / 1000.0) * z_lcl, 2)

    @staticmethod
    def lcl_height(temperature, dew_point):
        """
        Height of lifting condensation level.

        Approximation:
        z = (T - Td) * 125
        """

        if dew_point > temperature:
            raise ValueError("Invalid thermodynamic state")

        return int((temperature - dew_point) * 125)

    @staticmethod
    def lfc_height(parcel_temperature, lapse_rate):
        """
        Level of free convection height.
        """

        if lapse_rate <= 0:
            raise ValueError("Lapse rate must be positive")

        return int(parcel_temperature * lapse_rate * 0.6)

    @staticmethod
    def static_stability(environmental_lapse_rate, dry_lapse_rate):
        """
        Static stability.

        Difference between dry adiabatic
        and environmental lapse rate.
        """

        return round(dry_lapse_rate - environmental_lapse_rate, 1)
