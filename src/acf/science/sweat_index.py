"""
Severe Weather Threat Index (SWEAT)
===================================

Formula (Miller, 1972):

    SWEAT = 12*Td850 + 20*(TT-49) + 2*f850 + f500 + 125*(sin(dir500-dir850) + 0.2)

with term-clamping rules (verified against weather.cod.edu stability
indices reference and cross-checked with the standard SPC/AMS
definition — not reconstructed from memory alone):

    - Dewpoint term (12*Td850): zero if Td850 < 0 degC.
    - Total Totals term (20*(TT-49)): zero if TT < 49.
    - Wind shear term (125*(sin(...)+0.2)): zero unless ALL of:
        * 850 hPa wind direction in [130, 250] degrees
        * 500 hPa wind direction in [210, 310] degrees
        * (dir500 - dir850) > 0
        * both wind speeds >= 15 kt

Reference:
    Miller, R. C. (1972). "Notes on Analysis and Severe-Storm
    Forecasting Procedures of the Air Force Global Weather Central".
    AWS TR-200, Air Weather Service, USAF.
"""

import math


class SWEATIndex:
    """Severe Weather Threat Index."""

    @staticmethod
    def calculate(
        td850: float,
        tt: float,
        wind850: float,
        wind500: float,
        dir850: float,
        dir500: float,
    ) -> float:
        """
        Compute SWEAT Index.

        Parameters
        ----------
        td850 : Dew point at 850 hPa (°C)
        tt : Total Totals Index
        wind850 : Wind speed at 850 hPa (kt)
        wind500 : Wind speed at 500 hPa (kt)
        dir850 : Wind direction at 850 hPa (deg)
        dir500 : Wind direction at 500 hPa (deg)
        """
        dewpoint_term = 12.0 * max(td850, 0.0)
        tt_term = 20.0 * max(tt - 49.0, 0.0)
        wind_term = 2.0 * wind850 + wind500

        shear_conditions = (
            130.0 <= dir850 <= 250.0
            and 210.0 <= dir500 <= 310.0
            and (dir500 - dir850) > 0.0
            and wind850 >= 15.0
            and wind500 >= 15.0
        )
        if shear_conditions:
            shear_term = 125.0 * (math.sin(math.radians(dir500 - dir850)) + 0.2)
        else:
            shear_term = 0.0

        sweat = dewpoint_term + tt_term + wind_term + shear_term

        return max(sweat, 0.0)

    @staticmethod
    def category(value: float) -> str:

        if value < 150:
            return "Low"

        if value < 300:
            return "Moderate"

        if value < 400:
            return "High"

        return "Extreme"
