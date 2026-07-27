"""
ACF - Model4D Physics
Hurricane Dynamics Module

Atmospheric cyclone physics calculations.
"""


class HurricaneDynamicsPhysics:
    """
    Physics engine for hurricane dynamics.
    """

    @staticmethod
    def pressure_drop(initial_pressure, final_pressure):
        """
        Pressure decrease.

        Example:
        1010 - 950 = 60
        """
        return initial_pressure - final_pressure


    @staticmethod
    def wind_speed_from_pressure(pressure_drop):
        """
        Wind speed estimation from pressure drop.

        ACF simplified relation:
        V = sqrt(deltaP * 1.6)
        """
        return round((pressure_drop * 1.6) ** 0.5, 3)


    @staticmethod
    def wind_speed_from_pressure_drop(pressure_drop):
        """
        Alias compatibility.
        """
        return HurricaneDynamicsPhysics.wind_speed_from_pressure(
            pressure_drop
        )


    @staticmethod
    def hurricane_category(wind_speed):
        """
        Saffir-Simpson simplified category.
        """
        if wind_speed < 64:
            return 1
        elif wind_speed < 83:
            return 2
        elif wind_speed < 96:
            return 3
        elif wind_speed < 113:
            return 4
        else:
            return 5


    @staticmethod
    def eyewall_strength(wind_speed, factor):
        """
        Eyewall intensity index.
        """
        return wind_speed * factor


    @staticmethod
    def storm_surge_height(wind_speed, coefficient):
        """
        Storm surge estimation.
        """
        return wind_speed * coefficient


    @staticmethod
    def coriolis_force(speed, latitude_factor):
        """
        Simplified Coriolis effect.
        """
        return speed * latitude_factor


    @staticmethod
    def coriolis_effect(speed, latitude_factor):
        """
        Compatibility alias.
        """
        return HurricaneDynamicsPhysics.coriolis_force(
            speed,
            latitude_factor
        )


    @staticmethod
    def hurricane_energy(mass, velocity):
        """
        Simplified hurricane energy index.

        E = mass × velocity
        """
        return mass * velocity


    @staticmethod
    def rainfall_rate(amount, duration):
        """
        Rainfall rate.
        """
        return amount / duration


    @staticmethod
    def track_speed(distance, time):
        """
        Hurricane movement speed.
        """
        return distance / time


    @staticmethod
    def intensification_rate(old_pressure, new_pressure):
        """
        Pressure deepening rate.
        """
        return old_pressure - new_pressure
