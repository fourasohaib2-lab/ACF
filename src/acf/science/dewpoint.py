"""
Atmospheric Complexity Framework (ACF)

SCIENCE - Dewpoint

Purpose:
--------
Pure mathematical and thermodynamic formulations (CAPE, CIN, LCL, vorticity).

Responsibilities:
-----------------
• Manage dewpoint logic and state representations.
• Integrate with the science subsystem of the ACF scientific engine.

Major Components:
-----------------
• DewPoint

Dependencies:
-------------
• Python Standard Library and NumPy/Scientific Python Stack.
• Internal acf.science module infrastructure.

Scientific Context:
-------------------
Provides foundational capabilities for numerical weather prediction, atmospheric data processing,
physical modeling, and spatial-temporal analysis within the Atmospheric Complexity Framework.
"""

import math


class DewPoint:
    @staticmethod
    def calculate(temperature_c: float, relative_humidity: float) -> float:
        """
        Dewpoint temperature via the Magnus-Tetens approximation
        (Alduchov & Eskridge 1996 coefficients a=17.27, b=237.7).

        NOTE (correction): relative_humidity was undocumented here,
        while the sibling formula WetBulbTemperature.calculate() in
        this same package explicitly expects relative_humidity as a
        FRACTION in [0, 1] - the opposite convention from this
        function, which expects a PERCENTAGE in [0, 100] (the only
        real caller, science/moisture.py's dewpoint_temperature(),
        already respects this - its own parameter is named
        relative_humidity_percent - so no active bug was found, but
        the mismatched convention between sibling files with no
        docstring here to warn a future caller was a real latent
        footgun). Now documented explicitly, with input validation
        matching the pattern already used by sibling files (e.g.
        VaporPressure.calculate(), WetBulbTemperature.calculate()).

        Parameters
        ----------
        temperature_c : float
            Air temperature (degrees Celsius).
        relative_humidity : float
            Relative humidity as a PERCENTAGE in [0, 100] (not a
            fraction in [0, 1] - see NOTE above).

        Returns
        -------
        float
            Dewpoint temperature (degrees Celsius).
        """
        if not (0.0 < relative_humidity <= 100.0):
            raise ValueError("relative_humidity must be a percentage in (0, 100].")

        a = 17.27
        b = 237.7

        gamma = (a * temperature_c) / (b + temperature_c) + math.log(relative_humidity / 100.0)

        return (b * gamma) / (a - gamma)
