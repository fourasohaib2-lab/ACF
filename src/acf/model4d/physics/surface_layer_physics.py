class SurfaceLayerPhysics:
    """
    ACF Model 4D
    Surface Layer Atmospheric Physics Module

    Simplified physical parameterizations
    for numerical weather prediction.
    """

    @staticmethod
    def wind_profile(wind_speed, height):
        """
        Logarithmic wind profile.
        """
        return wind_speed * height / 10


    @staticmethod
    def roughness_length(surface_type):
        """
        Surface roughness length.
        """
        values = {
            "ocean": 0.0002,
            "grass": 0.03,
            "forest": 1.0,
            "urban": 2.0
        }

        return values.get(surface_type, 0.1)


    @staticmethod
    def friction_velocity(wind_speed, coefficient=0.1):
        """
        Friction velocity.
        """
        return wind_speed * coefficient


    @staticmethod
    def surface_flux(density, velocity, scalar):
        """
        Generic turbulent flux.
        """
        return density * velocity * scalar


    @staticmethod
    def heat_flux(temperature_difference, coefficient):
        """
        Sensible heat flux.
        """
        return temperature_difference * coefficient


    @staticmethod
    def momentum_flux(friction_velocity):
        """
        Momentum flux.
        """
        return friction_velocity ** 2


    @staticmethod
    def turbulence_intensity(velocity_variance, mean_velocity):
        """
        Turbulence intensity.
        """
        return velocity_variance / mean_velocity


    @staticmethod
    def monin_obukhov_length(temperature, friction_velocity):
        """
        Simplified Monin-Obukhov length.
        """
        return temperature / (friction_velocity + 1)


    @staticmethod
    def surface_temperature_gradient(surface_temperature,
                                    air_temperature):
        """
        Temperature gradient.
        """
        return surface_temperature - air_temperature


    @staticmethod
    def exchange_coefficient(momentum, stability):
        """
        Atmospheric exchange coefficient.
        """
        return momentum / (stability + 1)
