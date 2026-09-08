"""
ACF - Atmospheric Complexity Framework
Chemistry Coupling Physics Module

Couplage chimie-atmosphère :
- taux de réaction chimique
- production/destruction d'espèces
- couplage chimie-transport
- facteur de réactivité
"""


class ChemistryCouplingPhysics:
    """
    Physics engine for atmospheric chemistry coupling.
    """

    @staticmethod
    def reaction_rate(concentration, rate_constant):
        """
        Calcul du taux de réaction.

        R = k * C

        Retour :
        - taux de réaction
        """
        if concentration < 0:
            raise ValueError("Concentration must be positive")

        if rate_constant < 0:
            raise ValueError("Rate constant must be positive")

        return concentration * rate_constant

    @staticmethod
    def chemical_lifetime(concentration, loss_rate):
        """
        Temps de vie chimique.

        τ = C / L
        """
        if loss_rate <= 0:
            raise ValueError("Loss rate must be positive")

        return concentration / loss_rate

    @staticmethod
    def production_rate(source, sink):
        """
        Bilan production - destruction.

        Pnet = source - sink
        """
        return source - sink

    @staticmethod
    def chemistry_transport_coupling(chemistry, transport):
        """
        Facteur de couplage chimie-transport.

        simplification ACF :
        coupling = chemistry * transport
        """
        return chemistry * transport

    @staticmethod
    def photochemical_factor(solar_flux):
        """
        Facteur photochimique normalisé.

        F = sqrt(flux) / 10
        """
        if solar_flux < 0:
            raise ValueError("Solar flux must be positive")

        return (solar_flux**0.5) / 10

    @staticmethod
    def ozone_production(no2, sunlight):
        """
        Production simplifiée d'ozone.

        O3 = NO2 * facteur solaire
        """
        if no2 < 0:
            raise ValueError("NO2 must be positive")

        return no2 * ChemistryCouplingPhysics.photochemical_factor(sunlight)
