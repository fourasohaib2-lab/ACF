"""
ACF - Atmospheric Complexity Framework

Model4D Physics Module

Lightning Physics Module

Simplified atmospheric electrical processes:
- lightning potential index
- lightning energy
- flash density
- storm electrification
"""


class Lightning:
    """
    Atmospheric lightning physical processes.
    """

    @staticmethod
    def electric_energy(voltage, current, duration):
        """
        Lightning energy.

        E = V * I * t
        """
        if voltage < 0:
            raise ValueError("Voltage must be positive")

        if current < 0:
            raise ValueError("Current must be positive")

        if duration < 0:
            raise ValueError("Duration must be positive")

        return voltage * current * duration

    @staticmethod
    def flash_density(flashes, area):
        """
        Lightning flash density.

        D = flashes / area
        """
        if area <= 0:
            raise ValueError("Area must be positive")

        return flashes / area

    @staticmethod
    def storm_index(cape, moisture, instability):
        """
        Thunderstorm potential index.

        Simplified combination of:
        - CAPE
        - humidity
        - instability
        """
        if cape < 0:
            raise ValueError("CAPE must be positive")

        if moisture < 0:
            raise ValueError("Moisture must be positive")

        if instability < 0:
            raise ValueError("Instability must be positive")

        return cape * moisture * instability

    @staticmethod
    def charge_separation(cloud_water, ice_content):
        """
        Cloud electrical charge generation.

        Simplified cloud electrification.
        """
        if cloud_water < 0 or ice_content < 0:
            raise ValueError("Cloud parameters must be positive")

        return cloud_water * ice_content

    @staticmethod
    def lightning_probability(storm_index):
        """
        Normalize lightning probability.

        Range: 0 - 1
        """
        if storm_index < 0:
            raise ValueError("Storm index must be positive")

        probability = storm_index / (storm_index + 100)

        return min(probability, 1.0)
