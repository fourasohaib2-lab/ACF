"""
ACF Model4D - Cloud Microphysics Module

Basic atmospheric cloud microphysics equations:
- saturation mixing ratio
- relative humidity
- condensation
- cloud water evolution
"""


class CloudMicrophysics:
    """
    Cloud microphysics physical parameterizations.
    """

    @staticmethod
    def relative_humidity(actual_vapor, saturation_vapor):
        """
        Compute relative humidity (%).

        RH = (qv / qvs) * 100
        """
        if saturation_vapor == 0:
            return 0.0

        return (actual_vapor / saturation_vapor) * 100.0

    @staticmethod
    def saturation_deficit(saturation_vapor, actual_vapor):
        """
        Difference between saturation and actual vapor.
        """

        return saturation_vapor - actual_vapor

    @staticmethod
    def condensation_rate(qv, qvs, coefficient=1.0):
        """
        Simple condensation tendency.

        If vapor exceeds saturation:
        C = coefficient * (qv - qvs)

        Otherwise no condensation.
        """

        excess = qv - qvs

        if excess <= 0:
            return 0.0

        return coefficient * excess

    @staticmethod
    def cloud_water_update(qc, condensation, evaporation):
        """
        Update cloud water content.

        dq_c/dt = condensation - evaporation
        """

        return qc + condensation - evaporation

    @staticmethod
    def autoconversion(qc, threshold=1e-3, rate=1.0):
        """
        Conversion of cloud water into rain water.
        """

        if qc <= threshold:
            return 0.0

        return rate * (qc - threshold)
