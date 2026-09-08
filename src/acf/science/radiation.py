"""
Radiation
=========

General (non-cloud-specific) radiation physics: Stefan-Boltzmann,
Planck's law, Beer-Lambert extinction, and solar position (Spencer
1971). Cloud-specific radiative transfer (optical depth from LWP,
cloud albedo, cloud radiative forcing) already lives in
science/clouds/radiation.py's CloudRadiationEngine — not duplicated
here.

Also fixes a registry gap: science/laws/radiation.py's 'planck_law'
entry had no compute_func (NotImplementedError on .calculate()) —
wired to PlanckLaw.calculate() here.

References:
    Liou, K. N. (2002). "An Introduction to Atmospheric Radiation".
    Spencer, J. W. (1971). "Fourier series representation of the
    position of the sun". Search, 2(5), 172.
"""

import math

STEFAN_BOLTZMANN_SIGMA = 5.670374e-8  # W/(m^2 K^4)
PLANCK_H = 6.62607015e-34  # J*s
SPEED_OF_LIGHT_C = 2.99792458e8  # m/s
BOLTZMANN_K = 1.380649e-23  # J/K
SOLAR_CONSTANT_S0 = 1361.0  # W/m^2 (TOA solar irradiance at 1 AU)


class StefanBoltzmann:
    """Blackbody total radiant emittance."""

    @staticmethod
    def calculate(temperature_k: float, emissivity: float = 1.0) -> float:
        """
        E = emissivity * sigma * T^4

        Parameters
        ----------
        temperature_k : float
            Absolute temperature (K), > 0.
        emissivity : float
            Emissivity in [0, 1]. Defaults to 1 (ideal blackbody).

        Returns
        -------
        float
            Radiant emittance (W/m^2).
        """
        if temperature_k <= 0:
            raise ValueError("temperature_k must be positive.")
        if not (0.0 <= emissivity <= 1.0):
            raise ValueError("emissivity must be in [0, 1].")
        return emissivity * STEFAN_BOLTZMANN_SIGMA * temperature_k**4


class PlanckLaw:
    """Blackbody spectral radiance (Planck's law)."""

    @staticmethod
    def calculate(wavelength_m: float, temperature_k: float) -> float:
        """
        B_lambda(T) = (2*h*c^2 / lambda^5) / (exp(h*c/(lambda*k*T)) - 1)

        Parameters
        ----------
        wavelength_m : float
            Wavelength (m), > 0.
        temperature_k : float
            Absolute temperature (K), > 0.

        Returns
        -------
        float
            Spectral radiance (W / (m^2 sr m)).
        """
        if wavelength_m <= 0:
            raise ValueError("wavelength_m must be positive.")
        if temperature_k <= 0:
            raise ValueError("temperature_k must be positive.")

        numerator = 2.0 * PLANCK_H * SPEED_OF_LIGHT_C**2 / wavelength_m**5
        exponent = PLANCK_H * SPEED_OF_LIGHT_C / (wavelength_m * BOLTZMANN_K * temperature_k)
        return numerator / (math.exp(exponent) - 1.0)


class BeerLambert:
    """Radiative extinction through an absorbing/scattering medium."""

    @staticmethod
    def calculate(incident_intensity: float, optical_depth: float) -> float:
        """
        I = I0 * exp(-tau)

        Parameters
        ----------
        incident_intensity : float
            Incident intensity I0 (any consistent unit), >= 0.
        optical_depth : float
            Optical depth tau (dimensionless), >= 0.

        Returns
        -------
        float
            Transmitted intensity (same unit as incident_intensity).
        """
        if incident_intensity < 0:
            raise ValueError("incident_intensity must be non-negative.")
        if optical_depth < 0:
            raise ValueError("optical_depth must be non-negative.")
        return incident_intensity * math.exp(-optical_depth)


class SolarPosition:
    """Solar declination, equation of time, and zenith angle (Spencer 1971)."""

    @staticmethod
    def day_angle(day_of_year: int) -> float:
        """Day angle Gamma (radians) = 2*pi/365 * (day_of_year - 1)."""
        return (2.0 * math.pi / 365.0) * (day_of_year - 1)

    @staticmethod
    def declination_spencer71(day_of_year: int) -> float:
        """
        Solar declination (radians), Spencer (1971) Fourier series.
        Accurate to within ~0.0006 rad (<3 arcmin).

        Parameters
        ----------
        day_of_year : int
            Day of year, 1-366.

        Returns
        -------
        float
            Declination (radians).

        Reference
        ---------
        Spencer, J. W. (1971). Search, 2(5), 172. Coefficients
        verified against pvlib's declination_spencer71 implementation.
        """
        g = SolarPosition.day_angle(day_of_year)
        return (
            0.006918
            - 0.399912 * math.cos(g)
            + 0.070257 * math.sin(g)
            - 0.006758 * math.cos(2 * g)
            + 0.000907 * math.sin(2 * g)
            - 0.002697 * math.cos(3 * g)
            + 0.001480 * math.sin(3 * g)
        )

    @staticmethod
    def equation_of_time_spencer71(day_of_year: int) -> float:
        """
        Equation of time (minutes), Spencer (1971) Fourier series.
        Accurate to within ~35 seconds.

        Parameters
        ----------
        day_of_year : int
            Day of year, 1-366.

        Returns
        -------
        float
            Equation of time (minutes; add to mean solar time to get
            apparent solar time).

        Reference
        ---------
        Spencer, J. W. (1971). Search, 2(5), 172. Coefficients (in
        radians, converted to minutes via *229.18) verified against
        pvlib's equation_of_time_spencer71 implementation form.
        """
        g = SolarPosition.day_angle(day_of_year)
        eot_radians = (
            0.0000075
            + 0.001868 * math.cos(g)
            - 0.032077 * math.sin(g)
            - 0.014615 * math.cos(2 * g)
            - 0.040849 * math.sin(2 * g)
        )
        return eot_radians * 229.18

    @staticmethod
    def hour_angle_deg(solar_time_hours: float) -> float:
        """
        Hour angle (degrees) = 15 * (solar_time_hours - 12).
        Negative before solar noon, positive after.
        """
        return 15.0 * (solar_time_hours - 12.0)

    @staticmethod
    def zenith_angle_deg(latitude_deg: float, declination_rad: float, hour_angle_deg: float) -> float:
        """
        Solar zenith angle (degrees) from standard spherical
        astronomy: cos(zenith) = sin(lat)*sin(dec) + cos(lat)*cos(dec)*cos(H)

        Parameters
        ----------
        latitude_deg : float
            Observer latitude (degrees, -90 to 90).
        declination_rad : float
            Solar declination (radians), e.g. from declination_spencer71().
        hour_angle_deg : float
            Hour angle (degrees), e.g. from hour_angle_deg().

        Returns
        -------
        float
            Zenith angle (degrees), 0 = sun overhead, 90 = sun at
            horizon, >90 = sun below horizon.
        """
        if not (-90.0 <= latitude_deg <= 90.0):
            raise ValueError("latitude_deg must be in [-90, 90].")

        lat = math.radians(latitude_deg)
        h = math.radians(hour_angle_deg)
        cos_zenith = math.sin(lat) * math.sin(declination_rad) + math.cos(lat) * math.cos(declination_rad) * math.cos(h)
        cos_zenith = max(-1.0, min(1.0, cos_zenith))  # guard against tiny FP overshoot
        return math.degrees(math.acos(cos_zenith))

    @staticmethod
    def toa_irradiance(zenith_angle_deg: float, solar_constant_w_m2: float = SOLAR_CONSTANT_S0) -> float:
        """
        Top-of-atmosphere solar irradiance on a horizontal surface:
        S0 * cos(zenith), clipped to 0 when the sun is below the
        horizon (zenith > 90 deg). Does not account for Earth-Sun
        distance variation (eccentricity correction) — uses the mean
        solar constant as-is.

        Parameters
        ----------
        zenith_angle_deg : float
            Solar zenith angle (degrees).
        solar_constant_w_m2 : float
            Solar constant (W/m^2). Defaults to 1361 W/m^2.

        Returns
        -------
        float
            Irradiance (W/m^2), >= 0.
        """
        cos_zenith = math.cos(math.radians(zenith_angle_deg))
        return max(0.0, solar_constant_w_m2 * cos_zenith)
