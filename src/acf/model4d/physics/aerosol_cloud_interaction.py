"""
ACF - Atmospheric Complexity Framework

Aerosol Cloud Interaction Physics Module

Contains simplified physical parameterizations for:
- aerosol-cloud interaction
- cloud condensation nuclei (CCN)
- aerosol indirect effects
- droplet activation
- cloud albedo response
"""


class AerosolCloudInteractionPhysics:
    """
    Physics engine for aerosol-cloud coupling.
    """

    @staticmethod
    def ccn_activation(aerosol_number, supersaturation):
        """
        Estimate activated cloud condensation nuclei.

        Parameters
        ----------
        aerosol_number : float
            Aerosol concentration (#/cm3)

        supersaturation : float
            Supersaturation (%)

        Returns
        -------
        float
            Activated CCN fraction
        """

        if supersaturation < 0:
            raise ValueError("Supersaturation cannot be negative")

        if aerosol_number <= 0:
            raise ValueError("Aerosol number must be positive")

        activation = aerosol_number * (supersaturation / 100)

        return min(activation, aerosol_number)

    @staticmethod
    def droplet_number(ccn, efficiency):
        """
        Cloud droplet formation.

        Parameters
        ----------
        ccn : float
            Activated CCN

        efficiency : float
            Activation efficiency (0-1)

        Returns
        -------
        float
            Droplet number
        """

        if ccn < 0:
            raise ValueError("CCN cannot be negative")

        if efficiency < 0 or efficiency > 1:
            raise ValueError("Efficiency must be between 0 and 1")

        return ccn * efficiency

    @staticmethod
    def aerosol_indirect_effect(clean_albedo, polluted_albedo):
        """
        Estimate aerosol indirect radiative effect.

        Parameters
        ----------
        clean_albedo : float
            Cloud albedo without aerosols

        polluted_albedo : float
            Cloud albedo with aerosols

        Returns
        -------
        float
            Relative albedo change
        """

        if clean_albedo <= 0:
            raise ValueError("Invalid clean albedo")

        return (polluted_albedo - clean_albedo) / clean_albedo

    @staticmethod
    def cloud_albedo_response(droplet_number):
        """
        Simplified cloud albedo response.

        Parameters
        ----------
        droplet_number : float
            Cloud droplet concentration

        Returns
        -------
        float
            Cloud albedo factor
        """

        if droplet_number < 0:
            raise ValueError("Droplet number cannot be negative")

        return droplet_number / (droplet_number + 1000)

    @staticmethod
    def aerosol_scavenging_rate(concentration, precipitation):
        """
        Wet scavenging by precipitation.

        Parameters
        ----------
        concentration : float
            Aerosol concentration

        precipitation : float
            Rain rate

        Returns
        -------
        float
            Removed aerosol fraction
        """

        if concentration < 0:
            raise ValueError("Invalid concentration")

        if precipitation < 0:
            raise ValueError("Invalid precipitation")

        return concentration * precipitation / 100

    @staticmethod
    def cloud_lifetime_change(clean_lifetime, aerosol_loading):
        """
        Aerosol effect on cloud lifetime.

        """

        if clean_lifetime <= 0:
            raise ValueError("Invalid lifetime")

        if aerosol_loading < 0:
            raise ValueError("Invalid aerosol loading")

        return clean_lifetime * (1 + aerosol_loading / 100)
