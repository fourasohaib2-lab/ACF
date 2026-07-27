class LandSurfaceModelPhysics:
    """
    ACF Model 4D - Land Surface Model Physics Module
    Sprint 8.59
    """

    @staticmethod
    def soil_temperature(surface, variation):
        """
        Soil temperature evolution.
        """
        return surface + variation


    @staticmethod
    def surface_flux(energy, coefficient):
        """
        Surface energy flux.
        """
        return energy * coefficient


    @staticmethod
    def vegetation_effect(radiation, vegetation_factor):
        """
        Vegetation impact on radiation.
        """
        return radiation * vegetation_factor


    @staticmethod
    def snow_cover_effect(temperature, snow_factor):
        """
        Snow cover thermal effect.
        """
        return temperature * snow_factor


    @staticmethod
    def surface_albedo(radiation, albedo):
        """
        Reflected radiation by surface.
        """
        return radiation * albedo


    @staticmethod
    def root_zone_moisture(initial, loss):
        """
        Root zone soil moisture.
        """
        return initial - loss


    @staticmethod
    def roughness_length(wind, factor):
        """
        Surface roughness estimation.
        """
        return wind * factor


    @staticmethod
    def energy_balance(incoming, losses):
        """
        Surface energy balance.
        """
        return incoming - losses


    @staticmethod
    def water_balance(precipitation, evaporation):
        """
        Surface water balance.
        """
        return precipitation - evaporation


    @staticmethod
    def land_surface_response(forcing, sensitivity):
        """
        Land surface response to atmospheric forcing.
        """
        return forcing * sensitivity

