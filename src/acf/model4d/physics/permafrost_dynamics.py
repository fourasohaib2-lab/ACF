"""
ACF - Atmospheric Complexity Framework
Model4D Physics Module

Permafrost Dynamics Physics
Sprint 8.65

Simulation simplified des interactions:
- sol gelé permanent
- température du permafrost
- profondeur de dégel actif
- fonte de glace du sol
- émission carbone
- flux thermique du sol
"""


class PermafrostDynamicsPhysics:
    """
    Physique simplifiée du pergélisol.
    """

    @staticmethod
    def active_layer_depth(temperature, conductivity):
        """
        Profondeur couche active de dégel.

        Formule simplifiée:
        profondeur = température * conductivité

        Exemple:
        5 * 2 = 10
        """
        return temperature * conductivity

    @staticmethod
    def permafrost_temperature(surface_temperature, insulation):
        """
        Température interne du pergélisol.
        """
        return surface_temperature - insulation

    @staticmethod
    def thaw_rate(temperature, sensitivity):
        """
        Taux de fonte du pergélisol.
        """
        return temperature * sensitivity

    @staticmethod
    def ground_ice_loss(initial_ice, melted_ice):
        """
        Perte de glace du sol.
        """
        return initial_ice - melted_ice

    @staticmethod
    def thermal_flux(conductivity, gradient):
        """
        Flux thermique du sol.

        F = k * gradient
        """
        return conductivity * gradient

    @staticmethod
    def carbon_release(thawed_area, carbon_density):
        """
        Libération carbone après dégel.
        """
        return thawed_area * carbon_density

    @staticmethod
    def permafrost_stability(temperature):
        """
        Etat du pergélisol.

        <=0 stable
        >0 instable
        """
        if temperature <= 0:
            return "stable"
        return "unstable"

    @staticmethod
    def freeze_depth(winter_temperature, factor):
        """
        Profondeur de gel hivernal.
        """
        return abs(winter_temperature) * factor

    @staticmethod
    def soil_settlement(thaw_depth, coefficient):
        """
        Affaissement du sol après fonte.
        """
        return thaw_depth * coefficient

    @staticmethod
    def methane_emission(thawed_volume, methane_factor):
        """
        Emission méthane.
        """
        return thawed_volume * methane_factor
