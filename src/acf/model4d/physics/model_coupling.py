"""
ACF - Atmospheric Complexity Framework
Model Coupling Physics Module

Handles coupling between:
- atmosphere
- ocean
- land surface
- cryosphere
- chemistry
- radiation

Sprint 8.25
"""



class ModelCouplingPhysics:
    """
    Physics engine for multi-component model coupling.
    """

    @staticmethod
    def coupling_strength(atmosphere, ocean, land):
        """
        Calculate normalized coupling strength.

        Parameters
        ----------
        atmosphere : float
            Atmospheric contribution
        ocean : float
            Ocean contribution
        land : float
            Land contribution

        Returns
        -------
        float
            Coupling coefficient
        """

        values = [
            atmosphere,
            ocean,
            land
        ]

        if any(v < 0 for v in values):
            raise ValueError("Coupling values must be positive")

        total = sum(values)

        if total == 0:
            raise ValueError("Total coupling cannot be zero")

        return round(total / len(values), 4)


    @staticmethod
    def energy_exchange(surface_flux, ocean_flux):
        """
        Compute energy exchange between components.
        """

        if surface_flux < 0 or ocean_flux < 0:
            raise ValueError("Flux must be positive")

        return round(abs(surface_flux - ocean_flux), 4)


    @staticmethod
    def coupling_balance(atmosphere, ocean):
        """
        Determine coupling equilibrium.
        """

        difference = abs(atmosphere - ocean)

        if difference < 0.05:
            return "balanced"

        if atmosphere > ocean:
            return "atmosphere_dominant"

        return "ocean_dominant"


    @staticmethod
    def feedback_factor(initial, coupled):
        """
        Calculate feedback response.
        """

        if initial == 0:
            raise ValueError("Initial state cannot be zero")

        return round((coupled - initial) / initial, 4)


    @staticmethod
    def climate_system_index(
        atmosphere,
        ocean,
        land,
        cryosphere
    ):
        """
        Global coupled climate index.
        """

        components = [
            atmosphere,
            ocean,
            land,
            cryosphere
        ]

        if any(c < 0 for c in components):
            raise ValueError(
                "Climate components must be positive"
            )

        return round(
            sum(components) / len(components),
            4
        )
