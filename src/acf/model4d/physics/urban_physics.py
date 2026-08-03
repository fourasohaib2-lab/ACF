"""
ACF - Atmospheric Complexity Framework
Model4D Physics
Urban Physics Module

Simulation des interactions atmosphère-ville :
- îlot de chaleur urbain (Urban Heat Island)
- rugosité urbaine
- stockage thermique urbain
- flux urbains
- impact sur température locale
"""



class UrbanPhysics:
    """
    Physique urbaine pour modèles atmosphériques 4D.
    """

    @staticmethod
    def urban_heat_island(
        urban_temperature,
        rural_temperature
    ):
        """
        Calcule l'intensité de l'îlot de chaleur urbain.

        UHI = T_urban - T_rural
        """

        if urban_temperature < 0 or rural_temperature < 0:
            raise ValueError(
                "Temperature values must be positive"
            )

        return urban_temperature - rural_temperature


    @staticmethod
    def surface_storage(
        heat_capacity,
        temperature_change
    ):
        """
        Stockage thermique urbain.

        Q = C * ΔT
        """

        if heat_capacity <= 0:
            raise ValueError(
                "Heat capacity must be positive"
            )

        return heat_capacity * temperature_change


    @staticmethod
    def urban_roughness(
        building_height,
        street_width
    ):
        """
        Longueur de rugosité urbaine simplifiée.

        z0 = 0.1 * h / w
        """

        if building_height <= 0:
            raise ValueError(
                "Building height must be positive"
            )

        if street_width <= 0:
            raise ValueError(
                "Street width must be positive"
            )

        return (
            0.1 *
            building_height /
            street_width
        )


    @staticmethod
    def anthropogenic_flux(
        population_density,
        energy_consumption
    ):
        """
        Flux anthropique urbain.

        F = densité * consommation
        """

        if population_density < 0:
            raise ValueError(
                "Population density invalid"
            )

        if energy_consumption < 0:
            raise ValueError(
                "Energy consumption invalid"
            )

        return (
            population_density *
            energy_consumption
        )


    @staticmethod
    def classify_environment(
        heat_island_intensity
    ):
        """
        Classification thermique urbaine.
        """

        if heat_island_intensity < 1:
            return "weak"

        elif heat_island_intensity < 3:
            return "moderate"

        else:
            return "strong"


    @staticmethod
    def urban_temperature_response(
        radiation,
        albedo
    ):
        """
        Réponse thermique urbaine simplifiée.

        ΔT = radiation * (1-albedo)
        """

        if not 0 <= albedo <= 1:
            raise ValueError(
                "Albedo must be between 0 and 1"
            )

        return radiation * (1 - albedo)


    @staticmethod
    def evapotranspiration_reduction(
        vegetation_fraction
    ):
        """
        Réduction évapotranspiration due à urbanisation.
        """

        if not 0 <= vegetation_fraction <= 1:
            raise ValueError(
                "Vegetation fraction invalid"
            )

        return 1 - vegetation_fraction

