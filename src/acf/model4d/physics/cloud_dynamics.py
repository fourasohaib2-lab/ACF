"""
ACF - Atmospheric Complexity Framework

Cloud Dynamics Physics Module
Sprint 8.37
"""

import math


class AtmosphericDynamicsPhysics:
    """
    Physics calculations for atmospheric cloud dynamics.
    """

    @staticmethod
    def cloud_velocity(updraft, entrainment):
        """
        Calculate cloud vertical velocity.

        Parameters
        ----------
        updraft : float
        entrainment : float

        Returns
        -------
        float
        """

        if not 0 <= entrainment <= 1:
            raise ValueError("Invalid entrainment")

        return round(updraft * (1 - entrainment), 3)

    @staticmethod
    def cloud_growth(rate, time):
        """
        Cloud growth over time.
        """

        if time < 0:
            raise ValueError("Invalid time")

        return round(rate * time, 3)

    @staticmethod
    def condensation_rate(vapor_mass, time):
        """
        Condensation rate.
        """

        if time <= 0:
            raise ValueError("Invalid time")

        return round(vapor_mass / time, 3)

    @staticmethod
    def cloud_lifetime(water_content, precipitation_rate):
        """
        Cloud lifetime estimation.
        """

        if precipitation_rate <= 0:
            raise ValueError("Invalid precipitation rate")

        return round(water_content / precipitation_rate, 3)

    @staticmethod
    def cloud_base_height(temperature, dew_point):
        """
        Cloud base height.

        H = 125(T-Td)
        """

        if temperature < dew_point:
            raise ValueError("Invalid temperature")

        return round(125 * (temperature - dew_point), 0)

    @staticmethod
    def coriolis_force(wind_speed, latitude):
        """
        Coriolis acceleration.

        Formula:
        f = 2Ω sin(latitude)

        a = f × V

        NOTE (correction — Physics Guard): this method used to (1) use
        a non-standard "omega = 7.313e-5" ("calibrated for ACF", with
        no citation - the real, standard Earth angular velocity is
        7.2921159e-5 rad/s, correctly used elsewhere in this codebase,
        e.g. model4d/constants.py's OMEGA/EARTH_ROTATION and the
        sibling, already-tested
        model4d.physics.atmospheric_dynamics.AtmosphericDynamicsPhysics
        - note the identical class name in a different file, a genuine
        duplicate this session's RÈGLE D'OR check found), and (2)
        contained an explicit hardcoded escape hatch
        ("Special validation case / Used by ACF unit tests") returning
        a fixed 0.001032 for exactly wind_speed=10, latitude=45,
        instead of ever computing the real formula for that input - a
        textbook case of gaming a specific test input rather than
        implementing the physics correctly. This class had 0% real
        test coverage (test_cloud_dynamics.py, despite its name,
        imports AtmosphericDynamicsPhysics from atmospheric_dynamics.py,
        not this file), so the escape hatch was never actually
        exercised by any real assertion. Removed the escape hatch and
        corrected omega to the standard value. Not fabricated.
        """

        if wind_speed < 0:
            raise ValueError("Wind speed must be positive")

        if latitude < -90 or latitude > 90:
            raise ValueError("Latitude must be between -90 and 90")

        omega = 7.2921159e-5  # standard Earth angular velocity (rad/s)

        value = 2 * omega * math.sin(math.radians(latitude)) * wind_speed

        return round(value, 6)

    @staticmethod
    def cloud_entrainment(mixing_rate, environment_factor):
        """
        Calculate entrainment mixing.
        """

        if environment_factor <= 0:
            raise ValueError("Invalid environment factor")

        return round(mixing_rate / environment_factor, 3)

    @staticmethod
    def convective_cloud_energy(mass, temperature):
        """
        Simplified cloud thermal energy.
        """

        if mass < 0:
            raise ValueError("Invalid mass")

        cp = 1004

        return round(mass * cp * temperature / 1000, 3)

    @staticmethod
    def cloud_water_content(volume, density):
        """
        Liquid water content.
        """

        if volume <= 0:
            raise ValueError("Invalid volume")

        return round(density / volume, 3)

    @staticmethod
    def cloud_rise_time(height, velocity):
        """
        Cloud rising time.
        """

        if velocity <= 0:
            raise ValueError("Invalid velocity")

        return round(height / velocity, 3)

    @staticmethod
    def precipitation_efficiency(rainfall, available_water):
        """
        Precipitation efficiency.
        """

        if available_water <= 0:
            raise ValueError("Invalid water quantity")

        return round(rainfall / available_water, 3)
